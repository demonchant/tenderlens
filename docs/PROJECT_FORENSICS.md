# Existing-project forensics and corrective changes

**Inspected:** 9 October 2026. This workspace began as an earlier TenderLens concept spike. Its first implementation and web pages were not a valid baseline for a no-mock, live-testnet submission.

## Initial state found

- Python code extracted one notice from hand-authored `fixtures/synthetic_notices.jsonl`, scored hard-coded expected tender values, and generated `evidence/demo-run.json` in simulated mode.
- The interactive comparison page rendered a fabricated tender and fixed dates/value/eligibility text; the score page used a simulated `0.92` result and `0.68` weight.
- The mechanism docs described “same notice identifier” as a change chain, even though TED eForms documents use BT-758 to reference the notice/version being changed and change notices have their own identifier.
- Rules/status records said source probes and hackathon details were still unknown; the user's supplied verified event listing and the successful live API probes now supersede those claims.

## Corrections made

- Deleted the synthetic tender corpus and the local synthetic demo/evaluator command. Product data now comes only from live TED requests.
- Reclassified the earlier real same-procedure records as a negative linkage example, not a valid amendment pair.
- Implemented explicit change-reference traversal, bounded live-source API, real source hashes and direct TED links; captured one live chain with four notices and three explicit edges.
- Changed miner tasks to carry source identifiers and references only. A miner fetches TED independently; it does not receive validator gold records.
- Replaced synthetic score interaction with a scoring specification, source evidence status and explicit testnet-pending state.
- Added Bittensor v11 signed requests/responses, permit checks, rate/size limits, test-only network guard, durable idempotent score history and double-opt-in weight submission path. These are code-level changes, not testnet evidence.
- Rewrote the docs, rubric map, dependencies, deployment instructions, evidence register and project status to distinguish verified/live/planned/unknown.

## Residual findings

1. The source-linked task is deterministic and TED already exposes public structured data and alerts. Independent operator value remains unproven.
2. The code still requires real Linux testnet installation, public endpoint, registered neurons and chain receipts. No credentials were available during this work.
3. User workflow/value research, public repository, final demo, pitch, organizer confirmation of rules/form, and hackathon submission are outstanding.
4. The one retained real chain supports protocol tests only. It does not establish representative performance or factual quality across TED notices.
