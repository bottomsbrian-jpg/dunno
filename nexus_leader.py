import logging
import time
from datetime import datetime, timezone

log = logging.getLogger("nexus.leader")

MARKET_STATE = {
    "regime": "unknown",
    "btc_price": 0.0,
    "btc_change": 0.0,
    "eth_price": 0.0,
    "trend_score": 0,
    "updated_at": None,
}

def _fetch_prices(exchange):
    try:
        btc = exchange.fetch_ticker("BTC/USDT")
        eth = exchange.fetch_ticker("ETH/USDT")
        return btc, eth
    except Exception as e:
        log.warning("Price fetch failed: %s", e)
        return None, None

def _classify_regime(btc_change, eth_change):
    avg = (btc_change + eth_change) / 2
    vol = abs(btc_change - eth_change)
    if vol > 5: return "volatile", 0
    elif avg > 3: return "bull", 3
    elif avg > 1: return "bull", 2
    elif avg > 0: return "bull", 1
    elif avg > -1: return "ranging", 0
    elif avg > -3: return "bear", -2
    else: return "bear", -3

def run(is_live=False):
    log.info("Leader bot cycle. Mode: %s", "LIVE" if is_live else "PAPER")
    start = time.monotonic()
    try:
        import ccxt
        exchange = ccxt.binance({"enableRateLimit": True})
        btc_ticker, eth_ticker = _fetch_prices(exchange)
        if btc_ticker and eth_ticker:
            bp = float(btc_ticker["last"]); bc = float(btc_ticker.get("percentage") or 0)
            ep = float(eth_ticker["last"]); ec = float(eth_ticker.get("percentage") or 0)
            regime, trend = _classify_regime(bc, ec)
            MARKET_STATE.update({"regime": regime, "btc_price": bp, "btc_change": bc,
                "eth_price": ep, "trend_score": trend, "updated_at": datetime.now(timezone.utc).isoformat()})
            log.info("BTC=$%,.2f(%+.2f%%) ETH=$%,.2f(%+.2f%%) Regime=%s Trend=%+d", bp, bc, ep, ec, regime.upper(), trend)
        else:
            log.warning("Could not fetch prices.")
    except ImportError:
        MARKET_STATE.update({"regime": "ranging", "btc_price": 60000.0, "btc_change": 0.5,
            "eth_price": 3000.0, "trend_score": 1, "updated_at": datetime.now(timezone.utc).isoformat()})
    except Exception as e:
        log.error("Leader error: %s", e, exc_info=True); raise
    log.info("Leader done in %.2fs.", time.monotonic() - start)
