import logging
from datetime import datetime, timezone
log = logging.getLogger("nexus.bot10")
SYMBOLS=["BTC/USDT","ETH/USDT"]; VOL_THRESH=5.0

def run(is_live=False):
    log.info("[Bot10] Risk Monitor start.")
    try:
        import ccxt
        from nexus_leader import MARKET_STATE
        ex=ccxt.binance({"enableRateLimit":True})
        regime=MARKET_STATE.get("regime","unknown"); trend=MARKET_STATE.get("trend_score",0)
        for s in SYMBOLS:
            try:
                t=ex.fetch_ticker(s); p=float(t["last"]); c=float(t.get("percentage") or 0)
                log.info("[Bot10] %s $%,.2f %+.2f%%",s,p,c)
                if abs(c)>=VOL_THRESH: log.warning("[Bot10] HIGH VOL on %s %+.2f%%",s,c)
            except Exception as e: log.warning("[Bot10] Cannot fetch %s: %s",s,e)
        if regime=="volatile": log.warning("[Bot10] VOLATILE - reduce sizes.")
        elif regime=="bear" and trend<=-2: log.warning("[Bot10] STRONG BEAR trend=%+d",trend)
        elif regime=="bull" and trend>=2: log.info("[Bot10] STRONG BULL trend=%+d",trend)
        else: log.info("[Bot10] Risk OK Regime=%s Trend=%+d",regime,trend)
    except ImportError: log.warning("[Bot10] ccxt not available.")
    except Exception as e: log.error("[Bot10] Error: %s",e,exc_info=True)
