# Evidence provenance register

Evidence records are actual responses/requests from public TED, not generated procurement fixtures. Source data is reused under TED's [reuse terms](https://docs.ted.europa.eu/ODS/latest/reuse/index.html) and [legal notice](https://ted.europa.eu/en/legal-notice): official procurement notices may be reused unless restricted, metadata is CC0, editorial content is CC BY 4.0, and third-party works, identifiable people, and the TED logo have separate conditions. This repository retains a bounded field set, preserves source links, and does not use the TED logo.

- [`ted-live-web-verification-20261009.json`](ted-live-web-verification-20261009.json) is a live response through the running same-origin TenderLens API on 9 October 2026. It records the source retrieval time and four returned records / three explicit BT-758 links for `8-2026`. It is evidence of that API run, not a benchmark or testnet result.
- [`docker-live-web-verification-20261009.json`](docker-live-web-verification-20261009.json) records the rebuilt Linux container returning HTTP 200 and the same live TED chain through its API, plus Bittensor v11 module/auth/weighting import checks. It does not claim wallet-backed signing, registered miners, or any chain activity.

| File | Provenance | What it supports | What it does not support |
|---|---|---|---|
| `ted-explicit-amendment-chain.json` | Live TED Search API, retrieved 9 Oct 2026 using seed publication `8-2026`; request/response traversal completed by `tenderlens/ted.py` | One real prior notice and three real change notices connected by exact BT-758 references; per-record hashes and links | Representative corpus, precision/recall claims, user demand, miner performance, or Bittensor testnet operation |
| `ted-amendment-search-request.json` | Exact query expressions and field projection used for the live discovery | How to reproduce a bounded source lookup | A raw capture of every individual API response in the traversal |
| `ted-version-pair-request.json` / `ted-version-pair-response.json` | Earlier real TED query by shared notice identifier | Negative discovery: records grouped under one procedure/version family can have different notice types and must not automatically be called an amendment | A valid amendment pair. Do not score these records as BT-758-linked changes. |
| `ted-search-probe-request.json`, `ted-notice-metadata-probe.json`, `ted-notice-metadata-response.json` | Earlier live TED API probes retained from the concept spike | API response shape and source metadata during initial feasibility work | Current product results; requests may not match the current field projection. |

`tests/` derives expected values from the actual `ted-explicit-amendment-chain.json` source records. Test mutations change only the miner response under test; they do not invent substitute tender documents. The web application and miner always request current TED data and never fall back to the captured responses.

The capture at `8-2026` is one selected chain containing four notices and three explicit links. It establishes that the API exposes a workable relation for this chain only. No benchmark or user study has been run.
