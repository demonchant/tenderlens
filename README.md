# TenderLens Change Watch

**A live TED procurement notice amendment desk and Bittensor testnet subnet prototype.** People enter a TED publication number; TenderLens follows TED's explicit Change Notice Version Identifier references (BT-758), retrieves the linked source records, and displays their field-level differences with provenance hashes.

The subnet task asks each miner to independently fetch the two identified public TED notices, verify the amendment link, and return the changed fields, typed prior/current values, source record hashes, and evidence. A validator fetches the same source records independently and scores exact tuples, source grounding, protocol validity, and miner response signatures. Repeated scores become relative miner weights on the configured **test network only**.

## Current status — 9 October 2026

- **Live source probe: VERIFIED.** On 9 October 2026, the running Desk API fetched TED publication `8-2026` live and returned four records and three explicit amendment references. A new response capture is in [`evidence/ted-live-web-verification-20261009.json`](evidence/ted-live-web-verification-20261009.json). An earlier same-procedure pair was rejected as an invalid amendment link and retained as negative evidence.
- **Live desk: IMPLEMENTED.** No tender fixture, seeded result, or offline data fallback is present in the app. Source failures remain visible.
- **Miner and scoring code: IMPLEMENTED, not yet run against Bittensor.** The miner independently reads TED and uses Bittensor v11 signed requests, validator-permit checks, bounded inputs, rate limits, and signed response bodies. The validator independently reads TED and can aggregate one live round for a test subnet.
- **Testnet: NOT CONFIGURED / NOT VERIFIED.** This workspace has no registered subnet UID, miner/validator wallet configuration, public miner endpoint, or on-chain receipt. `.env` is local and ignored; fill its values only when those real resources are ready. No chain result is claimed.
- **Hackathon submission: NOT SUBMITTED.** The 20 September proposal checkpoint is past. The HackQuest listing still shows the final deadline as 19 October 2026 at 15:59 (timezone not shown); organizer rules beyond the published description and any prior proposal status need confirmation. A reviewed public GitHub repository is being prepared; no demo video, pitch recording, or submission receipt is present.

## Judge fast path

1. Start the service with the instructions below.
2. Enter a real TED publication number on the Desk page. Use `8-2026` to reproduce the retained evidence chain.
3. Check the live response timestamp, publication IDs, source links, hashes, and explicit amendment edges. Open the comparison page to inspect a linked pair.
4. Open Mechanism and Scoring to inspect the miner task, independent validator check, and frozen score contract. These pages disclose that Bittensor is not connected yet.
5. For a live subnet run, use a registered testnet subnet and wallets; run miner and validator using the testnet steps. Preserve the evaluation JSON and chain receipt.

The `8-2026` value is a **real TED publication**, not a synthetic tender; the frontend does not prefill it. The evaluation tests use the captured public TED response in `evidence/` so scoring invariants can be checked offline. The running app and miner never use the captured response as a fallback. The real-only recording sequence and pitch script are in [`docs/demo-and-pitch.md`](docs/demo-and-pitch.md).

## Architecture

```text
Browser ── same-origin API ── TED Search API
                                  │ explicit BT-758 reference
                         prior record ↔ change notice
                                  │
Validator ── signed testnet task: source IDs + reference ──► Miner
    │                                                       │
    ├── independent TED fetch and source hashes ◄───────────┤
    ├── tuple / evidence / signature scoring                │
    └── Bittensor v11 SetWeights (explicit testnet opt-in)  │
```

The browser performs live source lookup and structural comparison; it does **not** pretend to be a validator or display simulated scores. The validator CLI is the scored testnet path. See the [subnet proposal](docs/subnet-proposal.md), [scoring contract](docs/scoring.md), [rubric matrix](docs/rubric-matrix.md), and [phase record](docs/hackathon-analysis.md).

## Run the live desk

Requires Python 3.11–3.14 and network access to the public TED API.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
tenderlens-web
```

Open `http://127.0.0.1:8787`. Requests go to `https://api.ted.europa.eu/v3/notices/search`. There is no demo mode and no request is silently answered from saved data.

## Testnet path

Bittensor v11 mining/validating is not supported directly on Windows. The regular `pip install -e .` installs the live web desk without the chain SDK. Use the Linux Docker image or WSL2 for the miner and validator; it installs the pinned testnet extra. First register or obtain access to the test subnet and neurons, place only the required wallet files in a protected local path, then fill the ignored `.env` from `.env.example`.

```dotenv
BT_NETWORK=test
TL_NETUID=<registered test subnet UID>
BT_WALLET=<wallet name>
BT_WALLET_HOTKEY=<registered hotkey name>
BT_WALLET_PATH=<wallet directory>
BT_WALLET_PASSWORD=<only if the SDK requires it>
```

After configuring a registered testnet subnet and wallet, start the miner in Linux/WSL2/Docker (not directly on Windows):

```powershell
docker --context default compose --profile testnet up -d miner
```

The miner must be reachable from testnet validators and its endpoint must be served on the configured test subnet. Run one live evaluation (scores and weights are saved locally; no chain transaction by default):

```powershell
docker --context default compose --profile testnet run --rm validator tenderlens-validator 8-2026
```

Submitting weights requires both `TL_ENABLE_WEIGHT_SUBMISSION=true` in `.env` and the explicit `--submit` flag. The code refuses any network other than `test`, and refuses to submit if no miner scored above zero.

Docker commands are documented in [`docs/deployment.md`](docs/deployment.md). Testnet registration, public endpoint operation, validator permit, metagraph discovery, signed miner request, source hashes, response signatures, score report, and a read-back of chain weights all need real evidence before a testnet claim is made.

## Repository map

- `web/` — live-source editorial UI. Each page has a direct navigation link to every other page.
- `tenderlens/ted.py` — bounded TED Search API client, explicit amendment-link traversal, hashes, and structural delta.
- `tenderlens/miner.py` — signed Bittensor v11 miner API and independent TED fetch.
- `tenderlens/validator.py` — live testnet miner discovery, signed fan-out, independent scoring, and guarded weight submission.
- `tenderlens/scoring.py`, `protocol.py` — strict response checks, score components, and relative-weight normalization.
- `docs/` — event/rubric research, proposal, implementation and security record.
- `evidence/` — real TED responses, probes, and (when run) actual evaluation receipts. No synthetic procurement corpus is used.
- `.env` — ignored local settings; no credentials are committed.

## Verify

```powershell
python -m unittest discover -s tests -v
node web/check-pages.mjs
```

The Python tests evaluate protocol and scoring invariants using a captured **real TED amendment chain**. They do not contact a Bittensor chain and are not benchmark results. The UI link checker verifies page navigation and accessibility hooks only.

## Security and known limits

- The browser API accepts only bounded TED publication identifiers; it cannot fetch arbitrary URLs. TED responses have a 3 MB cap, a 10-second per-request timeout, a bounded amendment-chain traversal, and request rate limits.
- The miner verifies btauth/1 request signatures before parsing bodies, checks the caller's validator permit in the current metagraph, caps request/response size and request rate, and signs its canonical response with its hotkey. Wallet files are never part of the repository or browser bundle.
- The web service binds to loopback by default. The public miner API should be deployed behind operator-managed network controls; it carries public source data but must never expose wallet files or `.env`.
- The scoring truth is TED's returned structured field values, not full-document semantic interpretation. Human usefulness and whether miners provide meaningful differentiated work still require user validation and independent miners. A weak ecosystem-value finding remains open in the [phase record](docs/hackathon-analysis.md).
- A single captured chain is source-linkage evidence, not representative evaluation. No adoption, market-size, production, uptime, emissions, or accuracy claim is made.

## License

TenderLens code is MIT licensed. TED source data remains subject to TED's applicable reuse terms and attribution; source URLs are shown in the product.
