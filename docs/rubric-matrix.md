# Hackathon judging criteria → implementation and proof

**Event source:** [Bittensor Global Subnet Hackathon listing](https://www.hackquest.io/hackathons/Bittensor-Global-Subnet-Hackathon), checked 9 October 2026. The event supplies the seven criteria below but no criterion weights. Statuses distinguish working code from observed testnet behavior.

| Criterion | Judge intent | Engineering requirement | Implementation | Proof and demo beat | Status / point-loss risk |
|---|---|---|---|---|---|
| **Mechanism & Incentive Design** | Is the rewarded miner work useful, objectively measured and tied to relative rewards? | Live source-pair discovery/retrieval; fixed scoring; failed tasks penalized; repeated scores normalize to miner UID weights. | `tenderlens/ted.py`, `protocol.py`, `scoring.py`, `validator.py`; `docs/scoring.md` | Submit one real linked pair, show miner's source hashes/delta, validator components, resulting testnet `SetWeights` transaction and read-back. | **PARTIAL.** Code path exists. No live neurons/weights. Distributed value and score variance remain open. |
| **Technical Implementation** | Does software work end to end on the target network? | Same-origin real-data app, independently operated miner, validator, source/error handling, setup and deploy instructions. | `web/`, `tenderlens/`, Docker assets, `docs/deployment.md` | Fresh start → TED record → authenticated miner request → independently scored result → testnet receipt. | **PARTIAL.** TED API is verified; Bittensor package install/runtime and on-chain flow not run. |
| **Miner-Validator Architecture** | Are roles distinct and communicating as subnet participants? | Validator discovers miners on metagraph; signs bounded request; miner verifies caller/permit, independently fetches TED, signs response; validator verifies and scores. | `tenderlens/miner.py`, `miner_server.py`, `validator.py`; Bittensor v11 APIs | Show at least one registered miner and one permitted validator communicating via their published testnet endpoints, with identities visible. | **PARTIAL.** Architecture code is present; endpoint registration, metagraph and signed request/response still need real run. |
| **Evaluation & Scoring Quality** | Are outputs accurate, grounded, and safe under misses and false alarms? | Exact tuple precision/recall/F1, old/new source evidence, task/source identity, hashes and protocol validity; no LLM judge. | `tenderlens/scoring.py`, `protocol.py`, `tests/` | Show one exact actual TED pair; score a correct response and evidence mismatch/omission; disclose sample size and limitations. | **PARTIAL.** Ten local contract, invariant, and immutable-history tests pass on one retained real source chain; this is not a representative benchmark and has no testnet evaluation yet. |
| **Problem & Market Relevance** | Does a real procurement user need this output? | Help suppliers/analysts detect changes that can affect deadline, scope, eligibility, value, or participation. | Live TED lookup and source comparison in `web/` | Ask an actual user to find a real change notice and verify whether the linked delta saves work; capture feedback only with permission. | **UNKNOWN / RISK.** No interview or repeat-use evidence. TED already provides public structured data. |
| **Bittensor Ecosystem Value** | Does a subnet improve production of a digital commodity through independent miners/validators? | Independently run, geographically/technically distinct miners retrieve and verify amendment chains; validators reward exact results and availability. | Bittensor v11 request, permit, scoring, weight intent code | Compare independently operated miners on the same live tasks; show score/availability differences and chain rewards. | **UNKNOWN / HIGHEST RISK.** Duplicate deterministic work may not justify decentralization. Demonstrate the advantage or pivot. |
| **Scalability & Long-Term Potential** | Can source coverage, quality and operators grow sustainably? | Versioned source adapters, bounded traversal, observable rates/failures, persistent score history, reproducible sources and measured operating cost. | TED adapter and protocol v1; future path in proposal | Show measured chain sizes, timeout/throughput, operator count and source expansion only when observed. | **PARTIAL.** Current API limits are bounded; no throughput, cost, independent operators, or durable scoring-window evidence. |

## Claim-to-proof ledger

| Public claim | Observable behavior required | Implementation / evidence | Demo path | State |
|---|---|---|---|---|
| “Uses live TED data” | Requests current source; failure is visible; no fixture fallback | `tenderlens/ted.py`, `web/app.js`; actual [live API capture](../evidence/ted-live-web-verification-20261009.json) | Enter live publication, check retrieval time and source links | `VERIFIED` for live app API response; visual browser review pending |
| “Finds explicit amendment relations” | BT-758 links exact parent publication/version | `versions_for_publication`; 4 records / 3 real links; official [TED change notice docs](https://docs.ted.europa.eu/eforms/latest/schema/change-notice.html) | Enter `8-2026`, inspect relation and source IDs | `VERIFIED` for captured sample only |
| “Miner independently retrieves and returns a grounded delta” | Registered miner makes its own live TED request and signs the response | `tenderlens/miner.py` | Run miner on a registered testnet endpoint | `IMPLEMENTED / UNVERIFIED` |
| “Validator scores miners and forms relative weights” | Validator obtains independent source truth and submits weights | `validator.py`, `scoring.py` | Evaluate miners, inspect score file and chain receipt | `IMPLEMENTED / UNVERIFIED` |
| “Runs on Bittensor testnet” | Actual subnet, metagraph, signed traffic, valid permit and chain weight read-back | None yet | Testnet runbook | `NOT VERIFIED`; never current-tense marketing |
| “Useful to procurement users” | User confirms task relevance and repeat use | No user evidence | User discovery before final pitch | `UNKNOWN` |
| “A subnet is better than centralized TED tooling” | Independent operator results show resilience, availability or useful diversity | No comparison data | Side-by-side experiment | `UNKNOWN`; principal competition risk |

## Submission artifact checklist

| Required item from event listing | Current artifact | State |
|---|---|---|
| Subnet proposal | [`subnet-proposal.md`](subnet-proposal.md) | Updated draft; not evidence of checkpoint submission |
| Functional subnet/miner and validator on testnet | Code and deploy path | Not run; wallet/netuid/permit needed |
| Evidence mechanism works | Real TED source chain + scoring tests | Live source-link capture and ten local tests pass; miner, validator and testnet runs remain unverified |
| Public GitHub repository | `https://github.com/demonchant/tenderlens` | Pending reviewed commit push |
| Setup and technical documentation | README/docs | Local draft |
| Testnet deployment instructions | [`deployment.md`](deployment.md) | Local plan; exact subnet and endpoint not configured |
| Demo video and final pitch | None | Not created |
| Final form and receipt | None | Not submitted |
