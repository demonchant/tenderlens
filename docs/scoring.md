# Scoring and incentives

## Truth source

The validator retrieves source records from TED independently from miner requests. A task is valid only if the current notice's TED Change Notice Version Identifier (BT-758) explicitly identifies the prior publication/version. A similar title, shared procedure, nearby publication date, or shared but ambiguous identifier is not a label. TED Search API fields are projected to the documented task fields and hashed as returned. Missing fields remain absent; we do not impute values.

## Per-task score

For an exact tuple `(field path, prior typed value, current typed value)`, count a true positive only when all three equal the validator's independently derived source delta. JSON types are compared strictly (`true`, `1`, and `1.0` are distinct). Duplicate, malformed, extra and wrong tuples remain in the predicted denominator and therefore lower precision. Omitted tuples lower recall.

```text
P = TP / predicted tuples
R = TP / expected tuples
F1 = 2 × P × R / (P + R)    (0 when P + R = 0)
EvidencePrecision = exact two-sided source-evidence tuples / predicted tuples
TaskScore = 0.70 × F1 + 0.25 × EvidencePrecision + 0.05 × ProtocolValidity
```

For the no-prediction case with expected changes, precision and evidence precision are zero and recall is zero; an empty response cannot earn a high score. If the source pair has no differences, the task generator should skip it rather than reward universal abstention. The current validator only creates a task from a live explicit amendment link; source changes/no results are operational errors, never “no change.”

`ProtocolValidity` is one only when protocol version, exact task ID, publication pair, explicit source reference, source hashes, output bounds and required response structure pass. Otherwise the response's changes are discarded and protocol credit is zero. Miner HTTP failures and bad signatures receive zero for that task.

Evidence must equal the canonical TED source value on both sides. For a non-string source value the canonical representation is UTF-8 JSON with sorted keys and compact separators; strings remain exact. This verifies returned field values, not a quotation span in a complete tender document. The UI does not label canonical field values as document quotations.

## Rolling weights

`score_store.py` persists each actual result under `(netuid, miner hotkey, task_id)` in local SQLite. The first score recorded for a task is immutable: a repeated task cannot add a sample or rewrite its result. The latest 32 distinct tasks per hotkey form its rolling mean. Current active miner UIDs map to those means and are normalized to relative weights. Failed calls are stored at zero. A hotkey leaving and later returning carries its prior rows; UID reassignment to a different hotkey does not.

Weight submission uses the Bittensor v11 `SetWeights` intent on `BT_NETWORK=test` and a configured positive `TL_NETUID`. It requires `TL_ENABLE_WEIGHT_SUBMISSION=true` **and** a deliberate `--submit` invocation. The testnet returns the accepted state; code records a separate `weights_readback_verified` result after fetching the validator's chain row. A successful SDK transaction alone is not presented as independent read-back proof.

## Invariants and evaluation scope

The checked-in automated tests use actual source records in `evidence/ted-explicit-amendment-chain.json`. They derive expected tuples from a real explicit BT-758 edge. Wrong/missing evidence and omissions are protocol/scoring perturbations, not replacement tender records. Sample size is one chain (three change edges), chosen for mechanism checks; it cannot support accuracy, recall, market fit, or general TED coverage claims.

Before any accuracy claim, assemble a legally reusable, chronologically and type-stratified set of real amendment edges, independently inspect expected values, include missing-field and cancellation cases, and report exact denominators and per-error categories. Do not substitute hand-authored records or claim the one-chain sample is representative.

## Failure cases

| Condition | Validator / miner behavior | Weight consequence |
|---|---|---|
| TED API timeout, invalid JSON, or response above cap | Reject source task with explicit source failure | No task score; no success-shaped cached result |
| No explicit BT-758 relation / parent missing | Do not send a comparison task | No zero-diff label fabricated |
| Chain is truncated by time/count bound | Do not emit task | No incomplete graph treated as truth |
| Miner unavailable or exceeds timeout | Record task failure | Zero score |
| Signature, nonce, identity, reference, or hash mismatch | Reject response | Zero score |
| Incorrect/extra/duplicate changed field | Counts against precision | Lower score |
| Missing field tuple | Counts against recall | Lower score |
| Wrong evidence side | No evidence credit for tuple | Lower score |
| Every miner scores zero | Refuse testnet weight submission | No empty weight transaction |
