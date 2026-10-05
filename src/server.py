"""Local HTTP server for the Mortgage Application Readiness Assistant.

Serves evaluated JSON from data/applications.csv and static files from web/.
Does not approve or deny loans.
"""

from __future__ import annotations

import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from loader import load_applications
from readiness import evaluate_all, summarize

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"
CSV_PATH = ROOT / "data" / "applications.csv"
ADVISORY_NOTICE = (
    "Recommendations are advisory. A human operations analyst makes the "
    "final decision. This tool does not approve or deny mortgages. "
    "All sample data is synthetic, and risk thresholds are illustrative "
    "prototype assumptions rather than lender policy."
)


def applications_payload() -> dict:
    rows = load_applications(CSV_PATH)
    evaluated = evaluate_all(rows)
    return {
        "applications": evaluated,
        "summary": summarize(evaluated),
        "advisory_notice": ADVISORY_NOTICE,
    }


class ReadinessHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/applications":
            body = json.dumps(applications_payload()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, format, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))


def main(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), ReadinessHandler)
    print(f"Mortgage Readiness Assistant: http://{host}:{port}", flush=True)
    print("Advisory only. No loan approval or denial.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
