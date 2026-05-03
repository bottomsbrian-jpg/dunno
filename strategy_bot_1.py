import logging
log = logging.getLogger("nexus.bot1")
SYMBOL = "BTC/USDT"
RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT = 14, 30, 70

def _calc_rsi(closes, period=14):
    if len(closes) < period + 1: return 50.0
    gains, losses = [], []
    for i in range(1, period + 1):
        diff = closes[-i] - closes[-i - 1]
        (gains if diff > 0 else losses).append(abs(diff))
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 1e-10
    return 100 - (100 / (1 + avg_gain / avg_loss))

def run(is_live=False):
    log.info("[Bot1] RSI Momentum start.")
    try:
        import ccxt
        from nexus_leader import MARKET_STATE
        ex = ccxt.binance({"enableRateLimit": True})
        ohlcv = ex.fetch_ohlcv(SYMBOL, "1h", limit=RSI_PERIOD + 5)
        closes = [c[4] for c in ohlcv]
        rsi = _calc_rsi(closes)
        price = closes[-1]
        regime = MARKET_STATE.get("regime", "unknown")
        log.info("[Bot1] %s Price=$%,.2f RSI=%.2f Regime=%s", SYMBOL, price, rsi, regime)
        if rsi < RSI_OVERSOLD and regime != "bear":
            log.info("[Bot1] %s BUY @ $%,.2f RSI=%.1f oversold", "LIVE" if is_live else "PAPER", price, rsi)
        elif rsi > RSI_OVERBOUGHT and regime != "bull":
            log.info("[Bot1] %s SELL @ $%,.2f RSI=%.1f overbought", "LIVE" if is_live else "PAPER", price, rsi)
        else:
            log.info("[Bot1] No signal RSI=%.2f", rsi)
    except ImportError: log.warning("[Bot1] ccxt not available.")
    except Exception as e: log.error("[Bot1] Error: %s", e, exc_info=True)
