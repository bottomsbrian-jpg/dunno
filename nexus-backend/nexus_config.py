"""
nexus_config.py — Central configuration loader for NEXUS deployment.
Reads all settings from environment variables. Never hardcode secrets here.

TWO-KEY LIVE SAFETY:
  - Set NEXUS_TRADING_MODE=live   (first key)
  - Set NEXUS_LIVE_CONFIRMED=true  (second key)
  Both must be present to place real orders. Missing either → process exits.
"""
import os
import sys
import logging

log = logging.getLogger("nexus.config")

TRADING_MODE = os.getenv("NEXUS_TRADING_MODE", "paper").strip().lower()

if TRADING_MODE not in ("paper", "live"):
    log.critical("NEXUS_TRADING_MODE must be 'paper' or 'live'. Got: '%s'. Exiting.", TRADING_MODE)
    sys.exit(1)

IS_LIVE = TRADING_MODE == "live"

if IS_LIVE:
    LIVE_CONFIRMED = os.getenv("NEXUS_LIVE_CONFIRMED", "false").strip().lower()
    if LIVE_CONFIRMED != "true":
        log.critical(
            "Live trading requested but NEXUS_LIVE_CONFIRMED != 'true'. "
            "Set BOTH NEXUS_TRADING_MODE=live AND NEXUS_LIVE_CONFIRMED=true to arm live orders. "
            "Exiting to prevent accidental live execution."
        )
        sys.exit(1)
    log.warning("NEXUS armed in LIVE trading mode. Real orders WILL be placed.")
else:
    log.info("NEXUS running in PAPER mode. No real orders will be placed.")

EXCHANGE_CONFIGS = {
    "binance":  {"api_key": os.getenv("BINANCE_API_KEY", ""),  "api_secret": os.getenv("BINANCE_API_SECRET", ""),  "testnet": not IS_LIVE},
    "coinbase": {"api_key": os.getenv("COINBASE_API_KEY", ""), "api_secret": os.getenv("COINBASE_API_SECRET", ""), "testnet": not IS_LIVE},
    "kraken":   {"api_key": os.getenv("KRAKEN_API_KEY", ""),   "api_secret": os.getenv("KRAKEN_API_SECRET", "")},
    "bybit":    {"api_key": os.getenv("BYBIT_API_KEY", ""),    "api_secret": os.getenv("BYBIT_API_SECRET", ""),    "testnet": not IS_LIVE},
}

ALPACA_API_KEY    = os.getenv("ALPACA_API_KEY", "")
ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET", "")
ALPACA_BASE_URL   = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets" if not IS_LIVE else "https://api.alpaca.markets")
POLYGON_API_KEY   = os.getenv("POLYGON_API_KEY", "")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")

ALERT_EMAIL_ENABLED   = os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true"
SMTP_HOST             = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT             = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER             = os.getenv("SMTP_USER", "")
SMTP_PASSWORD         = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL_FROM      = os.getenv("ALERT_EMAIL_FROM", SMTP_USER)
ALERT_EMAIL_TO        = os.getenv("ALERT_EMAIL_TO", "")
ALERT_WEBHOOK_ENABLED = os.getenv("ALERT_WEBHOOK_ENABLED", "false").lower() == "true"
ALERT_WEBHOOK_URL     = os.getenv("ALERT_WEBHOOK_URL", "")

NEXUS_LEADER_INTERVAL_SECS = int(os.getenv("NEXUS_LEADER_INTERVAL_SECS", "60"))
BOT_INTERVAL_SECS          = int(os.getenv("BOT_INTERVAL_SECS", "30"))
BOT_STAGGER_SECS           = int(os.getenv("BOT_STAGGER_SECS", "3"))
MAX_CONSECUTIVE_FAILURES   = int(os.getenv("MAX_CONSECUTIVE_FAILURES", "3"))

HEALTHCHECK_PORT = int(os.getenv("PORT", os.getenv("HEALTHCHECK_PORT", "8080")))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE  = os.getenv("LOG_FILE", "")

_bot_names_env = os.getenv("NEXUS_BOT_NAMES", "")
BOT_NAMES = (
    [n.strip() for n in _bot_names_env.split(",") if n.strip()]
    if _bot_names_env
    else [f"strategy_bot_{i}" for i in range(1, 11)]
)

APP_ENV = os.getenv("APP_ENV", "production")