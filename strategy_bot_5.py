import logging
log = logging.getLogger("nexus.bot5")
SYMBOL = "ETH/USDT"
FAST,SLOW,SIGNAL=12,26,9

def _ema(closes,period):
    k=2/(period+1); e=closes[0]
    for c in closes[1:]: e=c*k+e*(1-k)
    return e

def run(is_live=False):
    log.info("[Bot5] MACD start.")
    try:
        import ccxt
        ex=ccxt.binance({"enableRateLimit":True})
        ohlcv=ex.fetch_ohlcv(SYMBOL,"4h",limit=SLOW+SIGNAL+10)
        closes=[c[4] for c in ohlcv]
        mn=_ema(closes,FAST)-_ema(closes,SLOW)
        mp=_ema(closes[:-1],FAST)-_ema(closes[:-1],SLOW)
        mv=[_ema(closes[:i+1],FAST)-_ema(closes[:i+1],SLOW) for i in range(len(closes))]
        sn=_ema(mv,SIGNAL); sp=_ema(mv[:-1],SIGNAL)
        price=closes[-1]
        log.info("[Bot5] %s Price=$%,.2f MACD=%.4f Signal=%.4f",SYMBOL,price,mn,sn)
        if mp<=sp and mn>sn: log.info("[Bot5] %s BUY @ $%,.2f MACD crossed up","LIVE" if is_live else "PAPER",price)
        elif mp>=sp and mn<sn: log.info("[Bot5] %s SELL @ $%,.2f MACD crossed down","LIVE" if is_live else "PAPER",price)
        else: log.info("[Bot5] No MACD crossover.")
    except ImportError: log.warning("[Bot5] ccxt not available.")
    except Exception as e: log.error("[Bot5] Error: %s",e,exc_info=True)
