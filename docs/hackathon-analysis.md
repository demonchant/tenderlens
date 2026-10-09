# Bittensor Global Subnet Hackathon — build record

**Checked:** 9 October 2026. **Final deadline shown on the event listing:** 19 October 2026, 15:59 (timezone not stated). The proposal checkpoint dated 20 September has passed. Submission status and whether the organizer accepts a late proposal are unknown. No form submission is recorded.

**Primary event source:** [Verified Bittensor Global Subnet Hackathon listing](https://www.hackquest.io/hackathons/Bittensor-Global-Subnet-Hackathon). It describes the $10,000 online program; asks for a credible subnet concept, miner tasks, validator scoring, incentives, working testnet implementation, evidence, public GitHub repository, demo video, and pitch; and lists the seven judging criteria mapped in [rubric-matrix.md](rubric-matrix.md). The organizer's detailed terms, exact final form fields, eligibility/team rules, timezone, late checkpoint policy, and current team registration status are not available in the materials captured here.

## Required initial report

### Selected concept

**TenderLens Change Watch:** a source-audited live feed of public procurement amendments. Given a real TED publication, miners independently retrieve the cited original and change notice, verify the explicit TED Change Notice Version Identifier (BT-758) link, and return changed structured fields, typed before/after values, evidence, and source-record hashes. Validators independently retrieve those records and score tuple accuracy, source grounding, protocol validity, task identity, and miner response signatures. A validator aggregates repeated scores and submits relative weights only to the explicitly configured Bittensor test network.

**Why this candidate:** TED provides a live, unauthenticated Search API; the data probe revealed that a shared procedure ID is insufficient to establish an amendment. eForms assigns a new notice identifier to a change notice and has BT-758 point to the source notice/version. TenderLens now follows that exact source relation. A real test resolved four records and three explicit links. See [evidence/README.md](../evidence/README.md) and [the captured chain](../evidence/ted-explicit-amendment-chain.json).

### Hardest promise and scope

The hardest promise is: **an independently operated miner can retrieve a real TED amendment pair and return a signed, exact, source-grounded delta that an independent validator can verify and score.** The current code covers live source access, reference traversal, miner route, independent validator retrieval/scoring, and guarded testnet weight intent. Only the TED API lookup/linkage has been run live from this workspace. Bittensor neurons, wallet signatures, testnet weights, and an independent second miner remain unverified. The product copy names those gaps.

The main strategic risk is that structured TED fields make the diff deterministic, and TED already exposes notice information. Bittensor's contribution must be demonstrated as independently operated retrieval, resilience, and competing source-verification implementations—not asserted as an advantage. If testnet miners produce no differentiated or user-valued outcome, the subnet premise fails and must be narrowed or pivoted.

### Candidates compared

| Candidate | Core work | Objective evaluation | Distinctness / risk | Decision |
|---|---|---|---|---|
| TenderLens Change Watch | Resolve live amendment links and produce verifiable notice deltas | Exact against the independent TED response and explicit source references | Procurement-specific and source-backed; value beyond TED's own structured API and distributed deployment still need proof | Selected, mechanism-risk monitored |
| PatchProof code mutation verification | Find bugs or kill mutations in submitted software | Unit/mutation test outcomes | Too close to the event's own Proven Testnet example; rejected to avoid a derivative concept | Reject |
| GridFlex forecast subnet | Forecast grid demand/renewables and score after outcomes settle | Numeric error after actual measurements | Long and licensed outcome path; poor ten-day testnet evidence timing | Reject |

The event's [Proven Testnet example](https://www.hackquest.io/hackathons/Bittensor-Global-Subnet-Hackathon) establishes a strong reference for clear tasks, objective evaluation, and working testnet flow; TenderLens reuses those mechanism qualities without reusing the software verification product domain. Competitor and substitute status remains in [competitive-analysis.md](competitive-analysis.md).

### Integration truth table

| Capability | Exact interface / version | Environment and observed result | Credentials | Failure behavior | Evidence |
|---|---|---|---|---|---|
| Resolve publication and fetch real TED records | `POST https://api.ted.europa.eu/v3/notices/search`, fields from the official TED field list | TED production, anonymous. A live publication lookup and BT-758 linked chain returned four records / three edges | None | Bounded 10-second requests, 3 MB response cap, invalid/incomplete chain produces no miner task | `evidence/ted-explicit-amendment-chain.json`; API contract: [TED Search API](https://docs.ted.europa.eu/api/latest/search.html) |
| Render source results and structural field delta | Same-origin `/api/versions`, Python standard-library HTTP server | Live API returned four records and three explicit links on 9 October from both the host process and rebuilt Docker image; browser visual review remains | None | No cached success path; response errors are visible | `tenderlens/web.py`, `web/app.js`; `evidence/ted-live-web-verification-20261009.json`, `evidence/docker-live-web-verification-20261009.json` |
| Authenticate miners and validators | Bittensor v11 `bt.http_auth.sign/verify`, hotkey-signed result | Code implemented against [signed-request guide](https://www.bittensor.com/docs/guides/signed-requests); not yet exercised with a live testnet neuron | Registered hotkey wallet | Reject invalid/stale/replayed signatures, non-validator callers, oversized requests, rate excess | `tenderlens/miner.py`, `tenderlens/validator.py` |
| Discover and score registered neurons | Bittensor v11 async `Subtensor.subnets.metagraph(netuid)` | Code implemented; no configured netuid or chain proof | Validator wallet and registered subnet | Refuse if validator permit absent, source link missing, miner unavailable, or report malformed | `tenderlens/validator.py` |
| Submit relative weights | Bittensor v11 `SetWeights` intent | Code path guarded; not run | Validator hotkey / test subnet | Requires `.env` opt-in plus CLI `--submit`; rejects any network except `test` and all-zero weights | `tenderlens/validator.py`; [SDK migration guide](https://www.bittensor.com/docs/migration) |

No sponsor technology is mandated in the event materials. TED is a public source dependency, not a sponsor, and is not described as one.

## Phase ledger (build-standard phases 0–9)

| Phase | Required artifact / exit condition | Current status | Evidence / open item |
|---|---|---|---|
| 0 — event and evidence intake | Official event, deadlines, rules, sources, constraints | **PARTIAL** | Event listing and criteria captured. Final form terms, eligibility details, team rules and timezone need direct organizer confirmation. Proposal checkpoint has passed; submission status unknown. |
| 1 — rubric engineering | Criterion → behavior → proof → demo → repo path → risk | **RECORDED** | [Rubric matrix](rubric-matrix.md). Testnet rows are deliberately not marked complete. |
| 2 — generate and gate ideas | Three candidates, scorecard, hard floor, risk spike | **RECORDED / CONDITIONAL** | [Idea gate](idea-gate.md), actual TED API probe, explicit amendment reference verified. User discovery and distributed-value proof remain open. |
| 3 — architecture | Roles, trust boundaries, data, failures, secrets, modes | **IMPLEMENTED AS CODE/DOCS** | [Proposal](subnet-proposal.md), [dependency audit](dependency-audit.md), `.env.example`, `.gitignore`. Actual network config still absent. |
| 4 — end-to-end proof | Hardest promise on intended environment with independent postcondition | **PARTIAL** | Live TED publication→explicit source links verified. Miner→validator→testnet transaction not yet run. |
| 5 — mechanism/data depth | Meaningful miner work, frozen scoring, measured error categories | **PARTIAL** | Real one-chain scoring invariants; no representative benchmark, human usefulness evidence, or quality estimate. No AI is claimed or required. |
| 6 — security/reliability | Abuse/failure boundaries and critical tests | **CODED / PARTIALLY VERIFIED** | Ten scoring/protocol/score-history tests, four-page link/accessibility check, Docker image build, app health/live-source route, and Bittensor SDK/auth/weighting imports pass. Hostile review, wallet-backed signatures and live testnet behavior remain unverified. |
| 7 — evidence/repository | Provenance, truthful README, setup, proof index, public repository | **PUBLIC REPOSITORY PUBLISHED / SUBMISSION PENDING** | [`demonchant/tenderlens`](https://github.com/demonchant/tenderlens), `main` at `a4fc08d`; actual TED snapshots and Docker run evidence documented. No demo or submission receipt yet. |
| 8 — UI/demo | Interactive reviewer path, mobile/accessibility, reproducible demo | **UI IMPLEMENTED / DEMO NOT CAPTURED** | Four pages, live request UI, direct links, animations and reduced-motion handling. Browser/device and final testnet demo remain. |
| 9 — competitive/adversarial review | Compare actual alternatives, record hard criticism, fix high-risk finding | **PARTIAL** | Proven example reviewed; TED is also the substitute for basic structured differences. User discovery and independent adversarial review remain. |

### Four mandatory gates

| Gate | Result |
|---|---|
| Hardest promise | **PARTIAL:** exact TED retrieval/linkage is real; testnet miner-to-validator acceptance and weight receipt are not proven. Current-tense claims stop at the verified API behavior. |
| Operational depth | **PARTIAL:** live notice relations, stale/ambiguous sources, missing links and changed records have explicit paths. Durable score aggregation and recovery after process restart need testnet operation. |
| Evidence | **PARTIAL:** n=1 real amendment chain, three explicit links, and real-record invariant tests. This does not estimate accuracy or market value. |
| Claim-to-proof | **RECORDED:** [rubric matrix](rubric-matrix.md) lists public claims and their implementation/evidence/status. Testnet, audience value, scalability and deployment claims remain open. |

## Current implementation plan to final deadline

1. Now: verify syntax, scoring invariant tests, all-page links, live API request, app behavior, and dependency install. Repair failed checks.
2. Immediately after credentials/subnet details are available: Linux/WSL/Docker testnet readiness, register/serve miners, discover validator, run one source-linked pair end to end, verify saved evidence and read back any weight receipt.
3. Before 19 Oct: recruit independent miners/validators if possible, measure per-miner score variance and repeat-task behavior, run adversarial review, improve user outcome based on evidence, capture a genuine demo, finalize public repo/pitch/form only after all actual results are recorded.

If an independent testnet flow cannot be completed before the deadline, do not present this as a full hackathon-compliant final submission. Record the blocker and submit only if the organizer confirms eligibility and accepts the actual completion level.

## Current unknowns and risks

- Testnet subnet UID, required miner/validator count, wallet hotkeys/permits/stake, serving IP/port, and owner-side weight/version settings are unknown.
- The 20 September proposal checkpoint is in the past; prior team submission and late acceptance are unknown.
- The final submission form and exact event rules were not included in the event description. Verify them before submitting.
- TED structured differences are reproducible, but user research and why buyers/suppliers need a separate network are absent.
- The captured chain is useful for code checks; it is one selected chain, not an unbiased or representative dataset.
- Public README must be synced to the actual release, public repository, demo video, testnet transaction and organizer submission state.
