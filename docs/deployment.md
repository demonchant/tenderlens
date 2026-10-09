# Build, local run, and Bittensor testnet deployment

## Local live TED desk

The web desk needs Python 3.11–3.14 and network access to TED. It binds to `127.0.0.1` by default:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
tenderlens-web
```

Open `http://127.0.0.1:8787`. The only source path is the live TED Search API. A TED timeout, invalid response, missing publication, or no explicit amendment link is shown to the user as such. Nothing seeds or substitutes a local record.

## Runtime environment

Copy the structure in `.env.example` into the ignored local `.env`; the repository already includes an ignored, blank `.env` shell. Keep secrets, wallet directory and validator score DB out of Git. Do not use mainnet credentials here.

| Variable | Purpose | Required for |
|---|---|---|
| `BT_NETWORK` | Must be `test`; code refuses other values | Miner / validator |
| `TL_NETUID` | Positive UID of the actual test subnet | Miner / validator |
| `BT_WALLET`, `BT_WALLET_HOTKEY`, `BT_WALLET_PATH` | Local registered hotkey wallet selector and path | Miner / validator |
| `BT_WALLET_PASSWORD` / `BT_WALLET_PASSWORD_FILE` | Optional SDK unlock value; do not commit | Only if needed by the real wallet |
| `TL_HOST`, `TL_PORT` | Local web service bind/port | Web |
| `TL_MINER_HOST`, `TL_MINER_PORT` | Miner bind/port | Miner |
| `TL_ENABLE_WEIGHT_SUBMISSION` | Second gate; default `false` | Validator `--submit` |
| `TL_SCORE_DB` | Optional path to durable real-task score history | Validator; defaults to `data/validator-scores.sqlite` |

The coldkey is not used by the miner. Bittensor wallet documentation warns that hotkey files contain plaintext signing material; mount only into the required process, read-only, and protect the host directory. Do not paste a mnemonic into `.env`.

## Linux Docker / WSL2

Bittensor documents mining/validating as unsupported directly on Windows. Run the testnet processes in Linux/WSL2 or Docker. The image runs as an unprivileged user, has a read-only application filesystem, drops Linux capabilities, sets `no-new-privileges`, mounts wallet files read-only, and exposes the web UI only on host loopback. The public miner port must be reachable from validators.

Build the image and run the live desk:

```powershell
docker --context default compose build
docker --context default compose up web
```

Configure the registered testnet subnet, wallet path, and miner port in `.env`, then launch the testnet miner profile:

```powershell
docker --context default compose --profile testnet up -d miner
```

The miner must run on a host validators can reach. Publish its endpoint on the actual registered subnet using the current Bittensor CLI/SDK (`serve-axon`/TLS option supported by the network); use the exact IP and port visible from outside Docker. Serving an endpoint does not start the HTTP process—the miner container must remain running.

Run one real source-linked validator round without a weight transaction:

```powershell
docker --context default compose --profile testnet run --rm validator tenderlens-validator 8-2026
```

After inspecting real miner reports and confirming the configured test subnet, weight submission requires both `TL_ENABLE_WEIGHT_SUBMISSION=true` and:

```powershell
docker --context default compose --profile testnet run --rm validator tenderlens-validator 8-2026 --submit
```

The validator stores actual source hashes and evaluation results in `evidence/runs/`, durable per-miner task history in `data/`, and tries an independent weight-row read-back after a successful `SetWeights` intent. A transaction success without that read-back is not marked verified.

## Testnet prerequisites and exact gates

Before attempting the miner/validator steps, obtain and verify:

1. The organizer's supported testnet and the actual target subnet UID; if creating a new subnet, its registration eligibility, costs, and registration availability.
2. Miner hotkey registered to that subnet, validator hotkey registered with validator permit and sufficient chain requirements, and actual test tokens/stake required to participate.
3. A reachable public miner IP/port and permission to publish its endpoint. Network security group/firewall must allow the chosen port only as needed.
4. Wallet files placed in a protected Linux path; only the operational hotkey should be mounted into the process. Keep coldkey operations off the miner host.
5. Confirm current v11 SDK, Subtensor runtime, subnet weight version/rate limits and commit-reveal behavior from chain state before trying to submit weights.

Do not register a subnet or sign any chain transaction until the actual target, costs, wallet, and transaction preview have been reviewed. A new subnet registration/serve/weight call is an external chain action and may consume tokens. This workspace currently has no testnet wallet values, UID, endpoints, or on-chain receipts.

## Ports, trust and operational controls

- The public TED API is anonymous and contains public procurement records; the miner will only query the fixed TED endpoint, not a task-provided URL.
- The local web server has strict same-origin CSP/security headers, no CORS access, no request-body logs, local IP rate limits and bounded source reads. Bind it behind an authenticated operator gateway before exposing the UI publicly.
- Bittensor hotkey-signed requests authenticate validator identity and bind the task bytes/path/recipient/nonce. Miner responses are separately hotkey-signed and checked against the metagraph miner key. The transport includes public source data only; network availability remains an operational dependency.
- Single-process miner mode retains anti-replay nonce state and rate limits in memory. Do not increase Uvicorn workers without replacing process-local nonce/rate state with shared storage.
- For Internet-facing deployment, put the service behind host firewall and operator-managed TLS/monitoring, preserve the advertised Bittensor endpoint, restrict SSH/admin paths, and never mount `.env` in the frontend container.
- `/health` reports service configuration only, not that TED or Bittensor is currently reachable. Actual live checks must use a TED request or metagraph query.

## Reproducible demo checklist

1. Record source publication, response retrieval timestamp, prior/current publication IDs, BT-758 relation, source hashes, git commit, network, netuid and miner/validator hotkeys (public IDs only).
2. Start fresh web, miner and validator processes; verify miner is in the testnet metagraph before making the request.
3. Enter a real TED publication, follow the linked record in UI, run the testnet validator, show signed response checks, score components and sample count.
4. If allowed and configured, submit weights once; independently read the validator's testnet weight row and preserve receipt.
5. Show one live dependency failure or a real low-quality response as an honest failure. Do not play a failure as a successful chain event.
6. Record the actual run JSON and demo/video; remove secret values. Do not replace unavailable live services with fixtures.
