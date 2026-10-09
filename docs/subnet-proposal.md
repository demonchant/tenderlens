# TenderLens Change Watch — subnet proposal

**Status:** hackathon proposal draft. The design uses real public TED data; a testnet deployment, independent miners, user validation, and on-chain results are not claimed yet.

## Problem and use case

TED publishes procurement notices and explicit change notices. A supplier tracking an open competition may need to notice a changed deadline, requirement, value, or process quickly. TED's eForms change-notice data includes a reference to the notice/version being changed (BT-758), the sections affected (BT-13716), descriptions, and reasons. TenderLens follows that declared relationship and presents the source values side by side. It never infers an amendment from a similar title or shared procedure identifier.

TED already exposes structured notice data and its public website. TenderLens's hypothesis is that a subnet of independently operated source retrievers and change verifiers can provide a resilient, auditable feed with scored operators. That advantage over direct TED access is **not proven** and is the primary product risk.

## Digital commodity

The subnet produces a **source-audited procurement change record**:

- exact prior and change notice publication IDs;
- explicit TED BT-758 relation;
- stable hash of each source record as retrieved;
- complete changed field paths and typed before/after values;
- source values supporting each side;
- miner hotkey signature, validator task identity, retrieval status and latency.

The current source projection covers notice type/title, change descriptions/reason, deadlines, estimated values/currency, buyer, selection criteria, and procedure type. Unsupported fields are not represented as a complete legal interpretation or a full-document diff.

## Roles and task flow

### Task selection

The validator uses the live TED Search API to select a notice with an explicit BT-758 reference. It independently resolves the prior publication and exact change publication, confirms the relation, stores source record hashes, and constructs a task ID from the relation and record hashes. No task is emitted when a source is absent, malformed, ambiguous, timed out, or the bounded chain traversal is incomplete.

### Miner

The validator sends a signed `POST /v1/compare` task containing only the prior publication, change publication, explicit reference and task ID. A miner independently fetches current source records from TED, confirms both IDs and the exact relation, computes the field delta and evidence, and signs the canonical response with its Bittensor hotkey. It does not receive validator source records or gold delta values.

Expected response fields:

```json
{
  "protocol": "1",
  "task_id": "<sha256>",
  "prior_publication": "<TED publication>",
  "current_publication": "<TED change publication>",
  "reference": "<BT-758 prior reference>",
  "miner_hotkey": "<registered miner hotkey>",
  "validator_hotkey": "<requesting validator hotkey>",
  "request_nonce": "<fresh Bittensor request nonce>",
  "source_task_sha256": "<sha256 of exact signed request bytes>",
  "prior_record_hash": "<sha256>",
  "current_record_hash": "<sha256>",
  "changes": [
    {
      "field": "<TED field path>",
      "prior": "<typed source value>",
      "current": "<typed source value>",
      "evidence": {"prior": "<canonical source value>", "current": "<canonical source value>"}
    }
  ],
  "miner_signature": "<hotkey signature over canonical response including the identity and request bindings above>"
}
```

The actual JSON values remain typed (the text above shows contract shape only); no hardcoded task result is shipped to the product.

### Validator

The validator discovers active miners from the configured testnet metagraph. It verifies miner responses against their metagraph hotkeys and validator request nonce, independently re-reads TED, and checks the exact BT-758 relation, publication IDs, source hashes, changed field/value tuples, evidence and protocol shape. A timed out, unreachable, invalid or incorrect miner receives zero for that task and a visible failure reason.

## Scoring and incentive logic

For one task:

`task_score = 0.70 × exact_tuple_F1 + 0.25 × evidence_precision + 0.05 × protocol_validity`

- A tuple is exact only when field path and both typed values equal the validator's independent TED-derived values.
- Precision penalizes invented or duplicate changes; recall penalizes omissions; F1 prevents one from hiding the other.
- Evidence precision gives credit only when both sides exactly match the expected source values; it is divided by the number of predicted tuples.
- Wrong source IDs/hashes, stale task IDs, malformed fields, invalid signature, or protocol errors invalidate the response and receive no protocol credit.
- Failure to respond within the request timeout or to reach the public source is zero for that task.

Validator score history uses unique `(netuid, miner hotkey, task ID)` rows in a local SQLite store. The first result for a task is immutable: a replay neither adds another sample nor rewrites the recorded score. The latest 32 distinct tasks per hotkey form the rolling average; only current active miner UIDs are normalized into a relative weight vector. `SetWeights` sends that vector to the configured test subnet after two explicit opt-ins: `.env` flag and CLI `--submit`. Bittensor subnet limits and consensus determine on-chain emissions. This policy is coded but has not been exercised on-chain.

## Security and source integrity

- Network is hard-locked to Bittensor `test`; no mainnet mode exists in validator/miner commands.
- Validator request signatures bind body, path, recipient, nonce and sender; miner accepts only current metagraph validators holding a permit.
- Miner response signature is verified against the published miner hotkey and bound to the task hash, validator identity and fresh request nonce.
- Request/response byte limits, public ID validation, TED response caps/timeouts, traversal count/time caps, API request rate limits and miner per-validator rate limits reduce abuse.
- No arbitrary URL is accepted from a miner task. TED source endpoint is fixed in code. Only fields returned by TED are processed.
- Wallet paths and passwords stay in ignored `.env`/wallet mounts; wallet volumes are read-only in Docker. Do not use coldkey files for routine miner work.
- The miner sends public TED records only. The task has no bidder private information or confidential procurement material.

See [security and deployment](deployment.md) and [dependency audit](dependency-audit.md).

## Users and ecosystem value

Expected users are suppliers and procurement analysts who monitor live notices. Their willingness to use the output has not yet been established. Bittensor value depends on real differences in retrieval availability, operator diversity, and independently verified performance; source records are public and structured, so the subnet must outperform the direct-source baseline through resilience or coverage. A central point-loss risk is that every miner may return the same deterministic result without a user-valued reason to distribute it.

## Evidence and demonstration

One live TED chain currently provides four real public records and three explicit amendment edges (publication `8-2026`); it validates field/link semantics and exercises scoring invariants. This is not representative market evidence, an accuracy measurement, a miner comparison, or a testnet receipt. No fake/synthetic procurement record is included. See [`evidence/README.md`](../evidence/README.md).

### Judge run path

1. Enter a real TED publication number in the desk.
2. Inspect live publication IDs, fetch time, linked BT-758 references, source URLs and hashes.
3. Choose one explicit edge and inspect all differences from TED's requested structured fields.
4. Run registered testnet miner and validator; compare signed response with independently fetched TED data.
5. Inspect component score, rolling-history sample count, weight proposal, submitted transaction, and independent chain read-back.

Steps 1–3 can be run after application start and TED is reachable. Steps 4–5 remain pending testnet configuration and have not been demonstrated.

## Roadmap

| Stage | Exit condition | State |
|---|---|---|
| Proposal | Exact tasks, roles, score, incentives, risks, ecosystem value | Draft complete; proposal checkpoint date passed; submission unknown |
| Local live source slice | Search a real source, follow explicit links, show field values/hashes | API probe verified; browser check pending |
| Miner/validator local protocol | Signed role-bound HTTP, independent source retrieval, deterministic checks and durable real score history | Code present; dependency/runtime test pending |
| Testnet | Registered test subnet, active miner(s), validator permit, signed request/response, transaction/read-back | Not configured |
| Competitive proof | Independent operator variance, latency/availability, direct TED baseline, user discovery | Not started |
| Final submission | Updated proposal, public repository, working testnet evidence, demo, pitch, form receipt | Not submitted |

## Pivot rules

Pivot before final claims if TED's explicit references cannot be reliably resolved; if response provenance cannot be independently verified; if no registered testnet path can be reached; or if user/operator evidence shows the distributed network adds no value beyond TED's direct API.
