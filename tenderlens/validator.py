"""One live TED evaluation round against registered Bittensor testnet miners."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import bittensor as bt
import httpx
from bittensor.wallet import Wallet
from bittensor.keyfiles import Keypair

from .protocol import CompareTask
from .score_store import record_round
from .scoring import normalize_weights, score_response
from .ted import make_reference_delta, task_record, versions_for_publication

ROOT = Path(__file__).resolve().parents[1]


def env_config() -> tuple[int, Wallet]:
    network = os.getenv("BT_NETWORK", "test")
    if network != "test":
        raise SystemExit("Safety stop: BT_NETWORK must be exactly 'test'; mainnet is not supported by TenderLens")
    try:
        netuid = int(os.environ["TL_NETUID"])
    except (KeyError, ValueError):
        raise SystemExit("Set TL_NETUID to the registered test subnet UID")
    if netuid <= 0:
        raise SystemExit("TL_NETUID must be a positive test subnet UID")
    name = os.getenv("BT_WALLET", "")
    hotkey = os.getenv("BT_WALLET_HOTKEY", "")
    if not name or not hotkey:
        raise SystemExit("Set BT_WALLET and BT_WALLET_HOTKEY to the registered validator wallet")
    wallet = Wallet(name=name, hotkey=hotkey, path=os.getenv("BT_WALLET_PATH") or None)
    return netuid, wallet


async def query_one(client: httpx.AsyncClient, wallet: Wallet, neuron, task: CompareTask) -> dict:
    if not neuron.axon:
        raise RuntimeError("miner has no published axon endpoint")
    endpoint = neuron.axon
    if not isinstance(endpoint, str) or ":" not in endpoint:
        raise RuntimeError("miner axon endpoint is invalid")
    body = json.dumps(task.as_dict(), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    path = "/v1/compare"
    headers = bt.http_auth.sign(wallet, method="POST", path=path, body=body,
                                receiver_ss58=neuron.hotkey)
    request_nonce = next((value for key, value in headers.items()
                          if key.lower() == "x-bittensor-nonce"), None)
    if not request_nonce:
        raise RuntimeError("Bittensor SDK did not include a request nonce")
    response = await client.post(f"http://{endpoint}{path}", content=body, headers=headers,
                                 timeout=httpx.Timeout(15, connect=4))
    if response.status_code != 200:
        raise RuntimeError(f"miner returned HTTP {response.status_code}")
    if len(response.content) > 262_144:
        raise RuntimeError("miner response exceeds the 256 KiB response cap")
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("miner response is not JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("miner response is not a JSON object")
    signature = payload.pop("miner_signature", None)
    if not isinstance(signature, str) or len(signature) != 128:
        raise RuntimeError("miner response signature is missing or malformed")
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    try:
        valid_signature = Keypair(ss58_address=neuron.hotkey).verify(canonical, bytes.fromhex(signature))
    except Exception as exc:
        raise RuntimeError("miner response signature could not be verified") from exc
    if not valid_signature:
        raise RuntimeError("miner response signature is invalid")
    if payload.get("miner_hotkey") != neuron.hotkey:
        raise RuntimeError("miner response identity does not match metagraph")
    if payload.get("validator_hotkey") != wallet.hotkey.ss58_address:
        raise RuntimeError("miner response is not bound to this validator")
    if payload.get("request_nonce") != request_nonce:
        raise RuntimeError("miner response is not bound to this request nonce")
    if payload.get("task_id") != task.task_id:
        raise RuntimeError("miner response belongs to a different task")
    if payload.get("source_task_sha256") != hashlib.sha256(body).hexdigest():
        raise RuntimeError("miner response does not match the submitted task bytes")
    return payload


async def evaluate(publication: str, submit: bool) -> Path:
    netuid, wallet = env_config()
    pair = versions_for_publication(publication)
    if not pair.get("pair_available"):
        raise SystemExit("TED returned no complete, explicitly linked amendment pair; no miner task was created")
    versions = pair["versions"]
    linked = max(pair["pairs"], key=lambda edge: str(versions[edge["current_index"]].get("PD") or ""))
    prior, current = versions[linked["prior_index"]], versions[linked["current_index"]]
    prior_values, current_values = task_record(prior), task_record(current)
    if not make_reference_delta(prior_values, current_values):
        raise SystemExit("The explicit change affects no field in protocol v1; no empty-diff task was created")
    task_seed = json.dumps([linked["reference"], prior["ND"], current["ND"],
                            prior["record_hash"], current["record_hash"]], separators=(",", ":"))
    task_id = hashlib.sha256(task_seed.encode()).hexdigest()
    task = CompareTask(task_id, "TED", prior["ND"], current["ND"], linked["reference"])

    async with bt.Subtensor(network="test") as chain:
        graph = await chain.subnets.metagraph(netuid=netuid)
        validators = [n for n in graph if n.hotkey == wallet.hotkey.ss58_address]
        if not validators or not validators[0].validator_permit:
            raise SystemExit("Configured hotkey has no validator permit on this test subnet")
        miners = [n for n in graph if n.active and n.axon and not n.validator_permit]
        if not miners:
            raise SystemExit("No active miners with published endpoints are available on the configured test subnet")
        async with httpx.AsyncClient() as http:
            async def run(neuron):
                try:
                    payload = await query_one(http, wallet, neuron, task)
                    scored = score_response(task, payload, prior["record_hash"], current["record_hash"],
                                            prior_values, current_values)
                    return neuron, {**scored, "status": "scored"}
                except Exception as exc:
                    return neuron, {"task_id": task_id, "score": 0.0, "status": "failed",
                                    "error": type(exc).__name__}
            evaluated = await asyncio.gather(*(run(n) for n in miners))

        history = record_round(netuid, [
            {"uid": neuron.uid, "hotkey": neuron.hotkey, "task_id": task_id,
             "score": float(result["score"])} for neuron, result in evaluated])
        rolling_by_uid = {history[neuron.hotkey]["uid"]: float(history[neuron.hotkey]["score"])
                          for neuron, _ in evaluated if neuron.hotkey in history}
        weight_by_uid = normalize_weights(rolling_by_uid)
        report = {
            "mode": "LIVE_TESTNET_EVALUATION", "network": "test", "netuid": netuid,
            "created_at": datetime.now(timezone.utc).isoformat(), "source": "TED Search API",
            "publication": publication, "notice_identifier": pair["notice_identifier"],
            "task_id": task_id, "change_reference": linked["reference"],
            "prior": {"publication": prior.get("ND"), "record_hash": prior["record_hash"]},
            "current": {"publication": current.get("ND"), "record_hash": current["record_hash"]},
            "miner_count": len(miners), "evaluated": [
                {"uid": n.uid, "hotkey": n.hotkey, **result, "weight": weight_by_uid.get(n.uid, 0.0)}
                | ({"rolling_score": history[n.hotkey]["score"],
                    "rolling_samples": history[n.hotkey]["samples"]} if n.hotkey in history else {})
                for n, result in evaluated], "weights_submitted": False,
            "weights_readback_verified": False,
        }
        if submit:
            if os.getenv("TL_ENABLE_WEIGHT_SUBMISSION", "false").lower() != "true":
                raise SystemExit("Set TL_ENABLE_WEIGHT_SUBMISSION=true in .env to permit testnet weight transactions")
            if not any(value > 0 for value in weight_by_uid.values()):
                raise SystemExit("All miner scores are zero; refusing to submit empty weights")
            try:
                result = await chain.execute(bt.SetWeights(netuid=netuid, weights=weight_by_uid), wallet)
                if not result.success:
                    report["submission_error"] = str(result.error)
                else:
                    report["weights_submitted"] = True
                    report["chain_result"] = str(result)
                    chain_rows = await chain.weights.weights(netuid=netuid)
                    actual = chain_rows.get(validators[0].uid, {})
                    checks = {uid: abs(float(actual.get(uid, 0.0)) - value) <= 0.02
                              for uid, value in weight_by_uid.items()}
                    report["weights_readback_verified"] = all(checks.values()) and bool(checks)
                    report["weight_readback"] = {"validator_uid": validators[0].uid,
                                                  "miner_weights": {str(uid): float(value)
                                                                    for uid, value in actual.items()},
                                                  "matches_proposal": checks}
            except Exception as exc:
                report["submission_error"] = type(exc).__name__

    out = ROOT / "evidence" / "runs"
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out / f"testnet-evaluation-{stamp}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("mode", "network", "netuid", "publication", "miner_count", "weights_submitted")}, indent=2))
    print(f"Evidence: {path.relative_to(ROOT)}")
    return path


def main() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    parser = argparse.ArgumentParser(description="Run one live TED-to-testnet validator round")
    parser.add_argument("publication", help="Real TED publication number, e.g. 123456-2026")
    parser.add_argument("--submit", action="store_true", help="Submit resulting weights to the configured Bittensor test subnet")
    args = parser.parse_args()
    asyncio.run(evaluate(args.publication, args.submit))


if __name__ == "__main__":
    main()
