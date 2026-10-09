"""Same-origin local web/API service; all procurement records come from live TED."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from dotenv import load_dotenv
from .ted import TedError, versions_for_publication

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = Path(os.getenv("TL_WEB_ROOT", str(ROOT / "web"))).resolve()
_rates: dict[str, list[float]] = {}
_rates_lock = threading.Lock()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        # No request bodies, hotkeys, or query parameters are logged.
        return

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'")
        super().end_headers()

    def do_GET(self):
        parts = urlsplit(self.path)
        try:
            if parts.path == "/api/health":
                self._json(200, {"service_status": "ok", "source_health": "not_checked",
                                 "source": "TED Search API", "data_mode": "live"})
                return
            if parts.path == "/api/versions":
                now = time.monotonic()
                address = self.client_address[0]
                with _rates_lock:
                    recent = [stamp for stamp in _rates.get(address, []) if stamp > now - 60]
                    if len(recent) >= 15:
                        self._json(429, {"error": "Live lookup rate limit reached; retry in a minute"})
                        return
                    recent.append(now)
                    _rates[address] = recent
                params = parse_qs(parts.query, strict_parsing=True)
                publications = params.get("publication", [])
                if len(publications) != 1 or len(params) != 1:
                    raise ValueError("Provide exactly one TED publication number")
                result = versions_for_publication(publications[0])
                self._json(200, result)
                return
        except ValueError as exc:
            self._json(400, {"error": str(exc), "source": "TED"})
            return
        except (TedError, ValueError) as exc:
            self._json(502, {"error": str(exc), "source": "TED"})
            return
        except Exception:
            self._json(502, {"error": "Live source request failed; no cached or fixture data was used", "source": "TED"})
            return
        if parts.path.startswith("/api/"):
            self._json(404, {"error": "Unknown API route"})
            return
        if parts.path == "/":
            self.path = "/index.html"
        elif not re.fullmatch(r"/(index|compare|mechanism|scoring)\.html|/styles\.css|/app\.js", parts.path):
            self._json(404, {"error": "Not found"})
            return
        return super().do_GET()

    def do_HEAD(self):
        self._json(405, {"error": "Method not allowed"})

    def _json(self, status: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    host = os.getenv("TL_HOST", "127.0.0.1")
    port = int(os.getenv("TL_PORT", "8787"))
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    print(f"TenderLens live TED desk listening at http://{host}:{port} (live source only)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
