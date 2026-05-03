import logging
log = logging.getLogger("nexus.bot6")
SYMBOL = "BTC/USDT"
LOOKBACK = 24

def run(is_live=False):
    log.info("[Bot6] Breakout start.")
    try:
        import ccxt
        ex=ccxt.binance({"enableRateLimit":True})
        ohlcv=ex.fetch_ohlcv(SYMBOL,"1h",limit=LOOKBACK+2)
        highs=[c[2] for c in ohlcv[:-1]]; lows=[c[3] for c in ohlcv[:-1]]
        price=ohlcv[-1][4]; res=max(highs[-LOOKBACK:]); sup=min(lows[-LOOKBACK:])
        log.info("[Bot6] %s Price=$%,.2f Res=$%,.2f Sup=$%,.2f",SYMBOL,price,res,sup)
        if price>res*1.001: log.info("[Bot6] %s BUY @ $%,.2f broke resistance","LIVE" if is_live else "PAPER",price)
        elif price<sup*0.999: log.info("[Bot6] %s SELL @ $%,.2f broke support","LIVE" if is_live else "PAPER",price)
        else: log.info("[Bot6] Inside range.")
    except ImportError: log.warning("[Bot6] ccxt not available.")
    except Exception as e: log.error("[Bot6] Error: %s",e,exc_info=True)
