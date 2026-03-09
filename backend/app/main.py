"""HTTP server entrypoint for ETF Relative Strength Dashboard backend."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.api.routes import get_dashboard_latest, get_metrics_latest, get_sparkline
from app.db.database import init_db


class ApiHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict | list) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health":
            return self._send_json(200, {"status": "ok"})
        if path == "/api/dashboard/latest":
            status, payload = get_dashboard_latest()
            return self._send_json(status, payload)
        if path == "/api/metrics/latest":
            status, payload = get_metrics_latest()
            return self._send_json(status, payload)
        if path.startswith("/api/prices/sparkline/"):
            symbol = path.rsplit("/", 1)[-1]
            status, payload = get_sparkline(symbol)
            return self._send_json(status, payload)

        return self._send_json(404, {"message": "Not found"})


def run() -> None:
    init_db()
    server = ThreadingHTTPServer(("0.0.0.0", 5000), ApiHandler)
    print("Backend running on http://localhost:5000")
    server.serve_forever()


if __name__ == "__main__":
    run()
