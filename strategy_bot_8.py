import logging
log = logging.getLogger("nexus.bot8")
SYMBOL = "BTC/USDT"

def _trend(ohlcv):
    closes=[c[4] for c in ohlcv]
    if len(closes)<10: return "neutral"
    ef=closes[-1]; k=2/11
    for c in reversed(closes[-10:]): ef=c*k+ef*(1-k)
    es=closes[-1]; k=2/21
    for c in reversed(closes[-20:] if len(closes)>=20 else closes): es=c*k+es*(1-k)
    if ef>es*1.001: return "up"
    if ef<es*0.999: return "down"
    return "neutral"

def run(is_live=False):
    log.info("[Bot8] Multi-TF start.")
    try:
        import ccxt
        ex=ccxt.binance({"enableRateLimit":True})
        o4=ex.fetch_ohlcv(SYMBOL,"4h",limit=25); o1=ex.fetch_ohlcv(SYMBOL,"1h",limit=25)
        t4=_trend(o4); t1=_trend(o1); price=o1[-1][4]
        log.info("[Bot8] %s Price=$%,.2f 4H=%s 1H=%s",SYMBOL,price,t4,t1)
        if t4=="up" and t1=="up": log.info("[Bot8] %s BUY @ $%,.2f both up","LIVE" if is_live else "PAPER",price)
        elif t4=="down" and t1=="down": log.info("[Bot8] %s SELL @ $%,.2f both down","LIVE" if is_live else "PAPER",price)
        else: log.info("[Bot8] Mixed no signal.")
    except ImportError: log.warning("[Bot8] ccxt not available.")
    except Exception as e: log.error("[Bot8] Error: %s",e,exc_info=True)
