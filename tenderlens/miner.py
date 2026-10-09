"""Bittensor v11 signed-request miner API for live TED version comparisons."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from collections import defaultdict, deque
from typing import Any

import bittensor as bt
from fastapi import FastAPI, HTTPException, Request
from bittensor.wallet import Wallet
from dotenv import load_dotenv
from tenderlens.ted import TedError, make_reference_delta, task_record, versions_for_publication

load_dotenv()
MAX_BODY = 262_144
MAX_REQ_PER_MIN = 20
try:
    NETUID = int(os.getenv("TL_NETUID") or "0")
except ValueError:
    NETUID = 0
WALLET_NAME = os.getenv("BT_WALLET", "")
WALLET_HOTKEY = os.getenv("BT_WALLET_HOTKEY", "")
WALLET_PATH = os.getenv("BT_WALLET_PATH") or None
NETWORK = os.getenv("BT_NETWORK", "test")
app = FastAPI(title="TenderLens Miner", docs_url=None, redoc_url=None, openapi_url=None)
_metagraph = None
_metagraph_at = 0.0
_rate: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = asyncio.Lock()
_metagraph_lock = asyncio.Lock()


async def _allowed(hotkey: str) -> bool:
    global _metagraph, _metagraph_at
    if _metagraph is None or time.monotonic() - _metagraph_at > 60:
        async with _metagraph_lock:
            if _metagraph is None or time.monotonic() - _metagraph_at > 60:
                try:
                    async with bt.Subtensor(network=NETWORK) as client:
                        _metagraph = await client.subnets.metagraph(netuid=NETUID)
                    _metagraph_at = time.monotonic()
                except Exception as exc:
                    raise HTTPException(503, "Testnet validator status cannot be verified") from exc
    neuron = _metagraph.by_hotkey(hotkey)
    return bool(neuron and neuron.validator_permit)


def _self_hotkey() -> str:
    if NETWORK != "test" or NETUID <= 0 or not WALLET_NAME or not WALLET_HOTKEY:
        raise HTTPException(503, "Miner is not configured for a registered Bittensor test subnet")
    try:
        return Wallet(name=WALLET_NAME, hotkey=WALLET_HOTKEY, path=WALLET_PATH).hotkey.ss58_address
    except Exception as exc:
        raise HTTPException(503, "Configured miner hotkey is unavailable") from exc


async def _authenticate(request: Request, body: bytes) -> str:
    hotkey = _self_hotkey()
    raw_path = request.scope.get("raw_path", request.url.path.encode("ascii"))
    query = request.scope.get("query_string", b"")
    target = raw_path.decode("ascii") + ("?" + query.decode("ascii") if query else "")
    try:
        caller = bt.http_auth.verify(request.headers, body, method=request.method,
                                     path=target, self_hotkey_ss58=hotkey)
    except bt.http_auth.AuthError as exc:
        raise HTTPException(401, "Invalid Bittensor request signature") from exc
    if not await _allowed(caller.hotkey_ss58):
        raise HTTPException(403, "Caller is not a validator on this test subnet")
    now = time.monotonic()
    async with _rate_lock:
        timestamps = _rate[caller.hotkey_ss58]
        while timestamps and timestamps[0] < now - 60:
            timestamps.popleft()
        if len(timestamps) >= MAX_REQ_PER_MIN:
            raise HTTPException(429, "Validator request limit exceeded")
        timestamps.append(now)
    return caller.hotkey_ss58


@app.get("/health")
async def health():
    ready = NETWORK == "test" and NETUID > 0 and bool(WALLET_NAME and WALLET_HOTKEY)
    return {"status": "configured" if ready else "not_configured", "network": NETWORK,
            "netuid": NETUID if NETUID > 0 else None, "protocol": "1"}


@app.post("/v1/compare")
async def compare(request: Request):
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        raise HTTPException(415, "Content-Type must be application/json")
    content_length = request.headers.get("content-length")
    if content_length and (not content_length.isdigit() or int(content_length) > MAX_BODY):
        raise HTTPException(413, "Task exceeds size limit")
    chunks: list[bytes] = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > MAX_BODY:
            raise HTTPException(413, "Task exceeds size limit")
        chunks.append(chunk)
    body = b"".join(chunks)
    caller = await _authenticate(request, body)
    try:
        task = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(400, "Task must be UTF-8 JSON") from exc
    if not isinstance(task, dict) or task.get("protocol") != "1":
        raise HTTPException(400, "Unsupported task protocol")
    task_id, source, prior_publication, current_publication, reference = (
        task.get(k) for k in ("task_id", "source", "prior_publication", "current_publication", "reference"))
    if not isinstance(task_id, str) or not (8 <= len(task_id) <= 100):
        raise HTTPException(400, "Invalid task identity")
    if not isinstance(source, str) or source != "TED":
        raise HTTPException(400, "Unsupported source")
    if not isinstance(prior_publication, str) or not isinstance(current_publication, str) or not isinstance(reference, str):
        raise HTTPException(400, "Source publications and explicit TED change reference are required")
    if len(prior_publication) > 20 or len(current_publication) > 20 or len(reference) > 80:
        raise HTTPException(400, "Source identifiers exceed protocol limits")
    if len(task_id) != 64 or any(char not in "0123456789abcdef" for char in task_id):
        raise HTTPException(400, "Invalid task identity")
    try:
        live_chain = await asyncio.to_thread(versions_for_publication, current_publication)
    except ValueError as exc:
        raise HTTPException(400, "Invalid TED publication reference") from exc
    except TedError as exc:
        raise HTTPException(503, "The live TED source could not be verified") from exc
    if live_chain.get("truncated"):
        raise HTTPException(503, "The live TED amendment chain is incomplete within source limits")
    edge = next((pair for pair in live_chain["pairs"]
                 if pair["reference"] == reference
                 and live_chain["versions"][pair["prior_index"]].get("ND") == prior_publication
                 and live_chain["versions"][pair["current_index"]].get("ND") == current_publication), None)
    if edge is None:
        raise HTTPException(409, "Live TED source no longer contains the requested amendment link")
    prior = live_chain["versions"][edge["prior_index"]]
    current = live_chain["versions"][edge["current_index"]]
    changes = make_reference_delta(task_record(prior), task_record(current))
    # Same task and same source payload always produce an auditable stable response.
    digest = hashlib.sha256(body).hexdigest()
    payload = {"protocol": "1", "task_id": task_id, "miner_hotkey": _self_hotkey(),
               "validator_hotkey": caller, "request_nonce": request.headers.get("X-Bittensor-Nonce"),
               "source_task_sha256": digest, "reference": reference,
               "prior_publication": prior_publication, "current_publication": current_publication,
               "prior_record_hash": prior["record_hash"], "current_record_hash": current["record_hash"],
               "changes": changes}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = Wallet(name=WALLET_NAME, hotkey=WALLET_HOTKEY, path=WALLET_PATH).hotkey.sign(canonical)
    return {**payload, "miner_signature": signature.hex()}
