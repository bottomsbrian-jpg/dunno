import logging
log = logging.getLogger("nexus.bot3")
SYMBOL = "BTC/USDT"
PERIOD, MULT = 20, 2.0

def _bands(closes, period, mult):
    w=closes[-period:]; mid=sum(w)/period
    std=(sum((c-mid)**2 for c in w)/period)**0.5
    return mid-mult*std, mid, mid+mult*std

def run(is_live=False):
    log.info("[Bot3] Bollinger Bands start.")
    try:
        import ccxt
        ex = ccxt.binance({"enableRateLimit": True})
        ohlcv = ex.fetch_ohlcv(SYMBOL, "4h", limit=PERIOD+5)
        closes=[c[4] for c in ohlcv]; price=closes[-1]
        lower,mid,upper=_bands(closes,PERIOD,MULT)
        log.info("[Bot3] %s Price=$%,.2f Lower=%.2f Upper=%.2f", SYMBOL, price, lower, upper)
        if price<=lower: log.info("[Bot3] %s BUY @ $%,.2f lower band", "LIVE" if is_live else "PAPER", price)
        elif price>=upper: log.info("[Bot3] %s SELL @ $%,.2f upper band", "LIVE" if is_live else "PAPER", price)
        else: log.info("[Bot3] Inside bands.")
    except ImportError: log.warning("[Bot3] ccxt not available.")
    except Exception as e: log.error("[Bot3] Error: %s", e, exc_info=True)
