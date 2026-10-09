# Competitive and substitute review

**Checked:** 9 October 2026. This is a first-pass product/feature check, not a claim of market uniqueness. Product statements below are limited to primary-source documentation and require a direct workflow comparison with users.

| Product / reference | Verified capability | Overlap / implication for TenderLens |
|---|---|---|
| [TED Search and Browse](https://ted.europa.eu/en/help/search-browse) | Free official source for current and historical notices. Its search controls include an “include only latest versions” option that surfaces latest changes and excludes old versions; it also documents signed-in search/notice alerts. | **Strongest substitute.** Users can already search/filter notices and receive alerts. TenderLens must prove that a cross-publication, explicit-reference change ledger with values/hashes adds meaningful review or integration value beyond TED's own UI/API. |
| [TED eForms change-notice model](https://docs.ted.europa.eu/eforms/latest/schema/change-notice.html) | Change notices contain BT-758 parent reference, affected sections, change descriptions and reasons. A change notice has its own notice ID. | TED's data semantics make exact linkage possible, but also provide an existing structured baseline. The subnet cannot claim it “solves missing TED version links” or supplies original ground truth. |
| [TED Open Data Service](https://data.ted.europa.eu/) | Public search/query platform for procurement information, sharing and downloading data. | A capable free research/data alternative. TenderLens must serve a specific amendment-monitoring workflow instead of being another generic procurement query UI. |
| [Mercell Bidding Platform](https://get.mercell.com/mercell-bidding-platform) | Product page describes users monitoring saved tenders through the platform. | Adjacent procurement monitoring; product-by-product amendment diff, source evidence, geographic coverage and price have not been audited. Avoid claiming TenderLens is the first tender-monitoring service. |
| [Proven Testnet](https://www.hackquest.io/hackathons/Bittensor-Global-Subnet-Hackathon) | Event example demonstrates software-verification tasks, validators, mutation testing, miners and a working testnet. | High mechanism overlap: objectively scored miner work. Procurement data is a different product domain, but TenderLens must match clarity, role separation and live testnet evidence. Do not copy its software-verification use case. |

## Differentiation and weak points

The narrow differentiated workflow to test is: resolve exact published change edges (including legacy publication-ID references and eForms UUID-version references), show every changed value with both record hashes, and let independently operated miners return the same task with verifiable provenance. One real chain demonstrates that the relation can be resolved; it does **not** prove users need it or that independent miners outperform one client.

The biggest counterargument is clear: TED itself exposes latest versions, search alerts and a reusable Search API. The current deterministic output could also be generated centrally from the same source. Bittensor's only plausible advantage here is independent retrieval resilience/coverage and verifiable participation; both require live multi-operator evidence. A single miner plus validator in testnet would prove architecture but not that subnet distribution is useful.

## Competitive tests still required

1. Ask a supplier or procurement analyst to complete their current amendment-check workflow using TED and one product they already use; record actual steps/time only with permission.
2. Compare one real amendment chain in TED, the user's incumbent tool, and TenderLens. Count unlinked versions, missed fields, source provenance and review time, without treating TED as a strawman.
3. Run the same source task through independent miners and a centralized baseline. Measure correctness, availability, retrieval freshness and latency with sample size and failures.
4. If results show TED and one parser already provide the full need, pivot the task to a harder, independently evaluable commodity or stop calling this a subnet advantage.
