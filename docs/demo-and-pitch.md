# Final demo and pitch runbook

**Status:** prepared, not recorded. This is an execution script for the real testnet build; it must not be recorded as complete until the testnet evidence exists.

## Preflight

1. Use Linux, WSL2, or the Linux Docker engine. Confirm `docker info` succeeds.
2. Obtain the event's accepted test network, subnet UID, validator/miner registration requirements, weight version/rate limits, and permission to use the target subnet.
3. Configure `.env` with only the required hotkey wallet paths/names, `BT_NETWORK=test`, actual `TL_NETUID`, miner port, and `TL_ENABLE_WEIGHT_SUBMISSION=false` for the first run. Keep `.env`, wallet files, coldkeys, and mnemonics out of the recording and repository.
4. Build and start the miner. Confirm its `/health` response says configured, then publish the reachable IP/port with the current Bittensor `serve-axon` flow.
5. Confirm the metagraph shows the miner endpoint and validator permit. Run a no-transaction validator round against a real TED publication that has an explicit BT-758 edge.
6. Inspect the actual JSON report: task/source IDs, hashes, miner hotkeys, signature checks, score components, failures, and rolling sample counts. Do not continue if it has no scored neurons or no source-linked task.
7. Only after reviewing the weight vector and confirming the test network, set `TL_ENABLE_WEIGHT_SUBMISSION=true`, run with `--submit`, and independently query the validator's weight row. Record the chain result and read-back. A transaction success without matching read-back is not a verified weight result.
8. Refresh the TED source from the UI once more. If TED or the chain is unavailable, record the failure and reschedule. Do not substitute saved evidence.

## Short demo sequence (about 3 minutes)

1. **Problem:** show a real public TED notice and explain that amendment lineage must be explicit; similar titles or procedure IDs do not establish a change.
2. **Live source:** enter its TED publication number in Desk. Show the actual retrieval time, linked records, TED source links, record hashes, and BT-758 relationship.
3. **Miner work:** show the registered miner endpoint in the metagraph, then the validator's signed task containing only the two source IDs and relation. Show the miner independently retrieves TED and returns its signed field delta.
4. **Evaluation:** show the validator's independent source retrieval and score components. Use only the actual report. Explain a real failed/incorrect response if one occurred; do not stage one as a successful evaluation.
5. **Incentives:** show the proposed relative weights, testnet transaction result, and independent weight-row read-back. Keep public hotkeys and receipt visible; hide wallet paths/secrets.
6. **Limits and roadmap:** state the measured sample count and operator count, explain what the evidence does not establish, and describe the next source/user validation step.

Record the source publication, retrieval timestamp, run-report filename, commit hash, network, netuid, public hotkeys, transaction block/hash, and read-back in `evidence/runs/`. The report itself is generated only by a real validator execution. Preserve the raw recording and submit a short edited copy only if the event permits editing.

## Pitch outline (about 90 seconds)

> Public procurement amendments can change a deadline, requirement, value, or process. TenderLens follows the public TED Change Notice Version Identifier to the exact notice version being changed, then shows the changed fields with direct source links and record hashes.
>
> Miners receive a bounded task containing source IDs and the explicit amendment reference. Each miner independently fetches TED and returns typed field changes with source evidence, signed to its Bittensor hotkey. Validators independently retrieve the same source records and score exact tuple precision and recall, evidence grounding, and protocol validity. Repeated task scores feed a bounded rolling mean and relative testnet weights; replaying a task cannot rewrite its first score.
>
> **Insert only measured results here:** `[number of registered miners]`, `[number of validators]`, `[actual scored tasks]`, `[observed score range]`, and `[weight transaction plus read-back evidence]`.
>
> The open question is whether independent operators add enough availability or verification diversity to justify a subnet over direct TED tooling. Our next step is to measure that with independently operated miners and procurement-user feedback.

The bracketed result fields are recording prompts, not example data. Replace them only with values from the actual testnet report and chain read-back. If those facts remain unavailable, the pitch and video are unfinished and must say so.

## Artifact record

| Required artifact | Current state | Completion proof |
|---|---|---|
| Fresh-session testnet demo video | Not recorded | Video visibly shows an actual miner-validator run and testnet read-back |
| Final pitch recording or presentation | Script prepared; not recorded | Contains measured results and honest limits from the actual run |
| Run evidence | Evidence folder prepared; no testnet receipt yet | JSON report plus independently checked chain result |
