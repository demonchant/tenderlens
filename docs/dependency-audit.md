# Dependency and integration audit

**Reviewed:** 9 October 2026. The source path and Python package versions are pinned in `pyproject.toml`; the live-web install passed on Windows, and the Linux testnet image built with the pinned Bittensor v11 SDK/core. Chain calls and actual testnet registration remain unverified.

| Dependency | Product job | Contract/version | Credentials | Failure behavior | State / evidence |
|---|---|---|---|---|---|
| TED Search API | Fetch public procurement notices and amendment references | Production `POST https://api.ted.europa.eu/v3/notices/search`; query `ND = <publication>` and `change-notice-version-identifier = "<reference>"`; fields listed in `ted.py`. Official [search docs](https://docs.ted.europa.eu/api/latest/search.html), [field list](https://docs.ted.europa.eu/ODS/latest/reuse/field-list.html) | None for public search | Fixed host; strict publication syntax; 10s request timeout; 3 MB cap; no fallback; reject incomplete/truncated chains | **Live probe verified**. Four actual records/three explicit links in [evidence](../evidence/ted-explicit-amendment-chain.json). |
| TED change-notice semantics | Prove parent/child relationship | BT-758 identifies notice/version being changed; the change notice has its own ID. [Official change-notice schema](https://docs.ted.europa.eu/eforms/latest/schema/change-notice.html) | None | Do not pair by same procedure ID, title or date | **Live sample verified**. Older misleading pair retained only as a negative discovery in evidence notes. |
| Bittensor SDK | Signed miner/validator requests, metagraph, `SetWeights` intent | Optional `testnet` extra pins `bittensor==11.3.0`; [v11 migration](https://www.bittensor.com/docs/migration), [signed requests](https://www.bittensor.com/docs/guides/signed-requests), [set weights](https://preview.bittensor.com/docs/tx/set-weights) | Registered testnet wallet/hotkey, subnet UID, validator permit and endpoint | Testnet lock, signed messages, per-task zero on failure, explicit guarded weight submission | **Linux image builds and SDK/auth/weighting imports pass; chain operations still need the user's subnet and registered wallets**. |
| FastAPI / Uvicorn / HTTPX | Miner endpoint and signed validator calls | `fastapi==0.143.0`, `uvicorn[standard]==0.53.0`, `httpx==0.28.1` | None by themselves | Timeouts, fixed route, no docs route, size/rate caps | **Pinned; Windows web dependencies and Linux image install pass**. |
| python-dotenv | Read local `.env` without bundling secrets | `python-dotenv==1.2.4` | Reads ignored `.env` file | Wallet config missing => fail closed | **Pinned; `.env` exists but is blank and ignored**. |
| SQLite | Durable, immutable first score per real task | Python stdlib; unique `(netuid, miner_hotkey, task_id)` key with `INSERT OR IGNORE`, rolling latest-32 distinct tasks | No credentials | Database failure stops validator before weight construction; data remains local | **Replay immutability test passes; process-restart operation remains unobserved**. |
| Docker | Repeatable Linux miner/validator environment | `python:3.12-slim`; unprivileged process, read-only app filesystem, dropped capabilities; context command pinned in deployment guide | Host wallet path mounted read-only | A missing wallet/netuid prevents testnet miner from becoming ready | **Image builds through the `default` Linux context; `desktop-linux` context currently errors with TLS bad-record-MAC**. |

## Provenance and terms

TED API results are public records, not TenderLens-created or synthetic data. The live product preserves source URLs and hashes and fetches current data on every lookup. A captured response is held as test evidence, never used to satisfy a live request. TED's [reuse documentation](https://docs.ted.europa.eu/ODS/latest/reuse/index.html) and [legal notice](https://ted.europa.eu/en/legal-notice) describe reuse and attribution terms: the notice permits reuse of official procurement notices absent a specific restriction, makes metadata available under CC0, and says editorial content is CC BY 4.0; identifiable people, third-party works, and the TED logo have separate restrictions. This repository captures only a narrow public sample for mechanism checks, links source records, and does not use the TED logo.

## Load-bearing integration table

| Claim | Exact request/operation | Observed request/result | Persistent/result artifact | What the dependency adds |
|---|---|---|---|---|
| Live source lookup | TED Search API v3, search by `ND` | Live `8-2026` request; response has 4 linked records / 3 explicit edges | `evidence/ted-explicit-amendment-chain.json` | Authentic public notice values and actual change-reference edges |
| Independent miner retrieval | Miner receives source IDs, then queries TED itself | Not yet exercised with a registered miner | Planned real evaluation report | Each independent miner returns its own source read and hash |
| Validator registration/discovery | v11 async metagraph | Not yet queried from configured netuid | No live metagraph capture | Confirms real network miner/validator identities and permits |
| Relative weight submission | `SetWeights(netuid, weights={uid: value})` | Not yet submitted | No chain receipt | Converts evaluator performance into on-chain relative validator weights |

No external LLM is used. No sponsor technology is required by the published event description. TED's API is a source integration, not sponsorship.
