# Idea gate — TenderLens Change Watch

**Decision date:** 9 October 2026. **Status:** source/API spike passed; testnet/value gate remains open. This is a build decision, not a claim that the final submission gate has passed.

## Candidate brief

- **User outcome:** notice the exact fields changed by an official TED procurement amendment, with the original and change notice visibly linked to TED's explicit reference.
- **Primary users:** suppliers monitoring opportunities and procurement analysts tracking amendments. Their pain and repeated-use frequency are plausible but have not been validated through interviews.
- **Miner task:** fetch the prior publication and amendment publication from live TED using the source IDs/reference in a signed task; verify the amendment reference; normalize and return changed typed fields, both source values, record hashes, and task-bound response signature.
- **Validator task:** independently fetch records from TED; require exact amendment relation and matching record hashes; derive truth from the structured source fields; score exact changed tuples, two-sided grounding and valid signed protocol; aggregate miner scores into relative weights.
- **Hardest promise:** a real miner independently fetches a live, source-linked change pair and a separate validator verifies and scores that output, with a testnet weight receipt.
- **Sponsor:** no required sponsor technology is present in the event listing; Bittensor testnet and miner/validator incentives are load-bearing event requirements. TED is a public source, not a sponsor.
- **AI:** not used. Structured TED fields plus deterministic comparison support objective scoring. Adding an LLM would obscure attribution without helping the exact task.
- **Differentiation to prove:** independently served, source-audited amendment retrieval and structured updates across a distributed operator network. Basic field comparison alone is available from TED and does not justify a subnet.
- **Riskiest unresolved assumption:** users value independently verifiable distributed retrieval, and miner diversity/availability improves on a direct TED query.
- **Deadline fit:** frontend and source adapter built; ten days remain to final deadline. A real subnet, registered neurons, public endpoints and demo still depend on testnet setup and independent operators.

## Scorecard

| Dimension | Score / 5 | Evidence and mitigation |
|---|---:|---|
| User pain and specificity | 3 | Concrete amendment-tracking job; no user interviews yet. Interview or document one real workflow before making adoption claims. |
| Rubric fit and eligibility confidence | 5 | Event explicitly asks for new subnet mechanism, miner/validator evaluation, testnet and incentive logic. Detailed eligibility/form still unknown. |
| Distinctive mechanism beyond a wrapper | 3 | Exact BT-758 source-link discovery, independent miner retrieval, source hashes and signed scoring exist; network advantage over TED's own API remains unproven. Compare live operator behavior before final pitch. |
| Hardest promise buildable and provable | 4 | TED query, exact parent references and persisted source record hashes were observed live; testnet flow is coded but not yet exercised. |
| Required sponsor tech load-bearing | 5 / N/A | No sponsor API/technology requirement in the event listing. Bittensor is central to the project and judging rubric. |
| Data/API/credential feasibility | 4 | Anonymous production TED Search API works. Testnet keys, UID, permit, endpoints and Windows/Linux operations remain unknown. |
| Evidence/evaluation practicality | 4 | Structured source values and explicit references allow deterministic scoring. Current retained sample is one real chain / three edges, not a benchmark. |
| Failure/recovery honesty | 4 | Missing, malformed, slow, oversized, ambiguous and truncated source paths reject the task; durable score-state recovery is not yet exercised. |
| Judge can understand and try it quickly | 4 | Real live lookup and source evidence are visible in four linked pages; testnet judge path is not yet available. |
| Scope fits actual team/time | 3 | Time is short and testnet credentials/independent operators are unknown. Cut optional coverage and stop short of submission claims if flow cannot be verified. |
| **Total** | **40 / 50** | Above planning threshold 35; mitigation needed for both 3/5 dimensions. |

## Mandatory floors

| Floor | Status | Evidence / action |
|---|---|---|
| Current official event, deadline, rules/form, eligibility | **Partial** | The listing and required artifacts/rubric are recorded. Final form fields, detailed terms, timezone, team eligibility and late checkpoint handling require organizer confirmation. |
| Specific user outcome | **Pass as hypothesis** | Amendment changes with source IDs and values. Validate the supplier/analyst workflow before claims of user demand. |
| Hardest promise observable | **Partial** | Acceptance path defined; live source stage passes; testnet neuron and weight stage open. |
| Riskiest API/data integration probed | **Pass for source lookup; partial for full source relation** | Live real pair with explicit BT-758 links captured. Miner-to-validator integration remains unprobed on-chain. |
| AI task or reason not to use AI | **Pass / N/A** | Deterministic structured comparison gives exact output and a stronger evaluation contract. |
| Mandatory sponsor work | **N/A** | No mandatory sponsor technology stated by event. Do not imply TED is event sponsor. |
| Demo and reviewer access by deadline | **Unknown** | UI path exists. Testnet requires available test subnet and registered neurons/accessible endpoint. |
| Legal, privacy, safety, reuse | **Partial** | Public TED records only; preserve links/attribution, check applicable TED reuse terms, avoid claiming legal advice. |

## Risk spike record

| Assumption | Probe and observed result | Decision |
|---|---|---|
| TED Search API is available without key and returns source records | Live request to production `POST /v3/notices/search`; publication `8-2026`; source response retained | Pass. No auth needed for this API request. |
| Shared notice IDs identify amendment pairs | Initial query showed related procedure-stage notices with the same ID; this is not sufficient for amendment lineage | Rejected. Same-ID grouping is not used as an amendment link. |
| BT-758 expresses the explicit change relation | Real search for `change-notice-version-identifier = *` and publication lookup yielded one parent plus three notices each explicitly referencing its predecessor | Pass for the captured chain. See evidence README and JSON. |
| Public TED HTML/XML access is a reliable miner source | Direct XML URL previously returned HTTP 405/CAPTCHA; the Search API metadata path works | Use only the Search API fields presently requested; do not claim full-document quotations or XML access. |
| Distributed miners create value beyond TED's basic API | No user interview, operator trial or comparative performance run yet | Open. If miners are identical and no independent-service advantage appears, pivot/narrow the commodity before final pitch. |

## Pivot conditions

1. If the source stops exposing explicit BT-758 references or stable record hashes, do not infer links from title or shared procedure identity. Reject that task.
2. If testnet miner/validator traffic and on-chain weights cannot be demonstrated, narrow the final claim to a source prototype and disclose the eligibility risk; do not claim a completed subnet.
3. If user research and distinct miner outcomes fail to support distributed retrieval, move to a harder source/format with independently testable work or select a different subnet idea before adding polish.
