import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    return {
        "NEXUS_TRADING_MODE": os.getenv("NEXUS_TRADING_MODE", "paper"),
        "NEXUS_LIVE_CONFIRMED": os.getenv("NEXUS_LIVE_CONFIRMED", "false"),
        "NEXUS_CYCLE_INTERVAL_SECONDS": os.getenv("NEXUS_CYCLE_INTERVAL_SECONDS", "3600"),
        "BINANCE_API_KEY": os.getenv("BINANCE_API_KEY", ""),
        "BINANCE_SECRET": os.getenv("BINANCE_SECRET", ""),
        "ALPACA_API_KEY": os.getenv("ALPACA_API_KEY", ""),
        "ALPACA_SECRET": os.getenv("ALPACA_SECRET", ""),
    }
