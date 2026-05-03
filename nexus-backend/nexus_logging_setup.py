"""
nexus_logging_setup.py — Structured logging for NEXUS. Import once at startup.
"""
import logging, logging.handlers, sys
import nexus_config as cfg

_FMT      = "%(asctime)s  %(levelname)-8s  [%(name)s]  %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"
_SUPPRESS = ["urllib3","ccxt","asyncio","requests","websocket","websockets","aiohttp"]

def _setup():
    root = logging.getLogger()
    root.setLevel(getattr(logging, cfg.LOG_LEVEL, logging.INFO))
    fmt = logging.Formatter(fmt=_FMT, datefmt=_DATE_FMT)
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(fmt)
    root.addHandler(h)
    if cfg.LOG_FILE:
        try:
            fh = logging.handlers.RotatingFileHandler(
                cfg.LOG_FILE, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
            fh.setFormatter(fmt)
            root.addHandler(fh)
        except OSError as e:
            root.warning("Could not open log file '%s': %s", cfg.LOG_FILE, e)
    for name in _SUPPRESS:
        logging.getLogger(name).setLevel(logging.WARNING)
    root.info("Logging ready. Level=%s | File=%s", cfg.LOG_LEVEL, cfg.LOG_FILE or "stdout only")

_setup()