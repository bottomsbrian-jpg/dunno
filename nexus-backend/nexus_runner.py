"""
nexus_runner.py — NEXUS main scheduler loop.
"""
import importlib
import logging
import signal
import sys
import threading
import time
from datetime import datetime, timezone

import nexus_config as cfg
import nexus_logging_setup  # noqa: F401
from nexus_alerting import alert
from nexus_health import start_health_server, mark_cycle_complete, mark_bot_status

log = logging.getLogger("nexus.runner")

_shutdown = threading.Event()

def _handle_signal(signum, _frame):
    sig_name = signal.Signals(signum).name
    log.warning("Received %s — initiating graceful shutdown.", sig_name)
    alert(f"NEXUS received {sig_name} — shutting down gracefully.", level="WARNING")
    _shutdown.set()

signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT,  _handle_signal)

def _load_bot(name):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as e:
        log.error("Cannot import bot module '%s': %s", name, e)
        return None

def _load_leader():
    try:
        return importlib.import_module("nexus_leader")
    except ModuleNotFoundError:
        log.warning("nexus_leader module not found — skipping leader step.")
        return None

def _run_leader(leader_module, leader_failures):
    if leader_module is None:
        return leader_failures
    start = time.monotonic()
    try:
        leader_module.run(is_live=cfg.IS_LIVE)
        log.info("Leader bot completed in %.2fs.", time.monotonic() - start)
        mark_bot_status("nexus_leader", "ok")
        return 0
    except Exception as exc:
        leader_failures += 1
        log.error("Leader bot failed (%d/%d): %s", leader_failures, cfg.MAX_CONSECUTIVE_FAILURES, exc, exc_info=True)
        mark_bot_status("nexus_leader", "error")
        alert(f"Leader bot failed ({leader_failures}/{cfg.MAX_CONSECUTIVE_FAILURES})",
              level="CRITICAL" if leader_failures >= cfg.MAX_CONSECUTIVE_FAILURES else "ERROR",
              exc=exc, bot_name="nexus_leader")
        if leader_failures >= cfg.MAX_CONSECUTIVE_FAILURES:
            log.critical("Leader bot failed %d times — exiting for auto-restart.", leader_failures)
            sys.exit(1)
        return leader_failures

def _run_strategy_bots(bot_modules):
    for i, (name, module) in enumerate(bot_modules.items()):
        if _shutdown.is_set():
            break
        if module is None:
            log.warning("Skipping '%s' — module failed to load.", name)
            continue
        if i > 0 and cfg.BOT_STAGGER_SECS > 0:
            time.sleep(cfg.BOT_STAGGER_SECS)
        start = time.monotonic()
        try:
            module.run(is_live=cfg.IS_LIVE)
            log.info("[%s] completed in %.2fs.", name, time.monotonic() - start)
            mark_bot_status(name, "ok")
        except Exception as exc:
            log.error("[%s] failed: %s", name, exc, exc_info=True)
            mark_bot_status(name, "error")
            alert(f"Strategy bot '{name}' raised an exception.", level="ERROR", exc=exc, bot_name=name)

def main():
    log.info("NEXUS starting | Mode: %s | Bots: %s", cfg.TRADING_MODE.upper(), ", ".join(cfg.BOT_NAMES))
    start_health_server(port=cfg.HEALTHCHECK_PORT, bot_names=cfg.BOT_NAMES)
    leader_module = _load_leader()
    bot_modules   = {name: _load_bot(name) for name in cfg.BOT_NAMES}
    missing = [n for n, m in bot_modules.items() if m is None]
    if missing:
        alert(f"Failed to import {len(missing)} bot module(s): {missing}", level="WARNING")
    leader_failures = 0
    cycle_number    = 0
    while not _shutdown.is_set():
        cycle_start  = time.monotonic()
        cycle_number += 1
        log.info("Cycle %d started at %s", cycle_number, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
        leader_failures = _run_leader(leader_module, leader_failures)
        _run_strategy_bots(bot_modules)
        mark_cycle_complete(cycle_number)
        elapsed   = time.monotonic() - cycle_start
        sleep_for = max(0, cfg.BOT_INTERVAL_SECS - elapsed)
        log.info("Cycle %d done in %.1fs. Sleeping %.1fs.", cycle_number, elapsed, sleep_for)
        _shutdown.wait(timeout=sleep_for)
    log.info("NEXUS shutdown complete.")

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        logging.critical("Unhandled exception in NEXUS main loop.", exc_info=True)
        alert("NEXUS main loop crashed with unhandled exception.", level="CRITICAL", exc=exc)
        sys.exit(1)