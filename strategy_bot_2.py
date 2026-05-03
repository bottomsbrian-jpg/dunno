import logging
log = logging.getLogger("nexus.bot2")
SYMBOL = "ETH/USDT"
FAST, SLOW = 9, 21

def _ema(closes, period):
    k = 2/(period+1); e = closes[0]
    for c in closes[1:]: e = c*k+e*(1-k)
    return e

def run(is_live=False):
    log.info("[Bot2] EMA Crossover start.")
    try:
        import ccxt
        ex = ccxt.binance({"enableRateLimit": True})
        ohlcv = ex.fetch_ohlcv(SYMBOL, "1h", limit=SLOW+10)
        closes = [c[4] for c in ohlcv]
        fn=_ema(closes,FAST); sn=_ema(closes,SLOW)
        fp=_ema(closes[:-1],FAST); sp=_ema(closes[:-1],SLOW)
        price=closes[-1]
        log.info("[Bot2] %s Price=$%,.2f EMA%d=%.2f EMA%d=%.2f", SYMBOL, price, FAST, fn, SLOW, sn)
        if fp<=sp and fn>sn: log.info("[Bot2] %s BUY @ $%,.2f EMA crossed up", "LIVE" if is_live else "PAPER", price)
        elif fp>=sp and fn<sn: log.info("[Bot2] %s SELL @ $%,.2f EMA crossed down", "LIVE" if is_live else "PAPER", price)
        else: log.info("[Bot2] No crossover.")
    except ImportError: log.warning("[Bot2] ccxt not available.")
    except Exception as e: log.error("[Bot2] Error: %s", e, exc_info=True)
