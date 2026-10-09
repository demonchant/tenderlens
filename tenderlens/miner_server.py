"""Start the Bittensor miner API with deployment settings loaded from .env."""

from __future__ import annotations

import os

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    if os.getenv("BT_NETWORK", "test") != "test":
        raise SystemExit("Safety stop: TenderLens miner serves testnet only")
    if not os.getenv("TL_NETUID", "").isdigit() or int(os.environ["TL_NETUID"]) <= 0:
        raise SystemExit("Set TL_NETUID to the registered Bittensor test subnet UID")
    import uvicorn
    uvicorn.run("tenderlens.miner:app", host=os.getenv("TL_MINER_HOST", "0.0.0.0"),
                port=int(os.getenv("TL_MINER_PORT", "8091")), workers=1, proxy_headers=False,
                server_header=False)


if __name__ == "__main__":
    main()
