"""
nexus_health.py — Lightweight HTTP healthcheck server for NEXUS.
Endpoints: GET /health  GET /status  GET /
"""
import json
import logging
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict

import nexus_config as cfg

log = logging.getLogger("nexus.health")

STALE_THRESHOLD_SECS = int(cfg.BOT_INTERVAL_SECS * 3)

_lock             = threading.Lock()
_last_cycle_ts: float = 0.0
_last_cycle_num: int  = 0
_bot_statuses: Dict[str, str] = {}
_start_time: float = time.monotonic()

def mark_cycle_complete(cycle_number: int) -> None:
    with _lock:
        global _last_cycle_ts, _last_cycle_num
        _last_cycle_ts  = time.monotonic()
        _last_cycle_num = cycle_number

def mark_bot_status(bot_name: str, status: str) -> None:
    with _lock:
        _bot_statuses[bot_name] = status

class _HealthHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def _send_json(self, code, payload):
        body = json.dumps(payload, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, code, text):
        body = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            self._send_text(200, "NEXUS is running.\n")
        elif path == "/health":
            with _lock:
                cycle_ts  = _last_cycle_ts
                cycle_num = _last_cycle_num
                statuses  = dict(_bot_statuses)
            now        = time.monotonic()
            secs_since = int(now - cycle_ts) if cycle_ts else 999999
            is_stale   = secs_since > STALE_THRESHOLD_SECS
            any_error  = any(v == "error" for v in statuses.values())
            overall    = "degraded" if any_error else ("stale" if is_stale else "ok")
            self._send_json(200 if overall == "ok" else 503, {
                "status": overall, "cycle": cycle_num,
                "secs_since_cycle": secs_since, "stale_threshold": STALE_THRESHOLD_SECS,
                "mode": cfg.TRADING_MODE, "uptime_secs": int(now - _start_time),
                "utc_time": datetime.now(timezone.utc).isoformat(),
                "bot_errors": [k for k, v in statuses.items() if v == "error"],
            })
        elif path == "/status":
            with _lock:
                statuses  = dict(_bot_statuses)
                cycle_num = _last_cycle_num
            self._send_json(200, {"cycle": cycle_num, "mode": cfg.TRADING_MODE,
                                  "bots": statuses, "utc_time": datetime.now(timezone.utc).isoformat()})
        else:
            self._send_text(404, "Not found.\n")

def start_health_server(port: int, bot_names: list) -> None:
    with _lock:
        for name in bot_names:
            _bot_statuses.setdefault(name, "unknown")
        _bot_statuses.setdefault("nexus_leader", "unknown")
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True, name="HealthServer")
    thread.start()
    log.info("Healthcheck server on 0.0.0.0:%d  (/ | /health | /status)", port)