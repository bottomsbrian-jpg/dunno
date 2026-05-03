import logging
log = logging.getLogger("nexus.bot4")
SYMBOL = "BTC/USDT"
LOOKBACK, SPIKE_MULT = 20, 2.5

def run(is_live=False):
    log.info("[Bot4] Volume Spike start.")
    try:
        import ccxt
        from nexus_leader import MARKET_STATE
        ex = ccxt.binance({"enableRateLimit": True})
        ohlcv = ex.fetch_ohlcv(SYMBOL, "1h", limit=LOOKBACK+2)
        vols=[c[5] for c in ohlcv]; prices=[c[4] for c in ohlcv]
        cv=vols[-1]; avg=sum(vols[-LOOKBACK-1:-1])/LOOKBACK
        ratio=cv/avg if avg else 0; price=prices[-1]
        regime=MARKET_STATE.get("regime","unknown")
        log.info("[Bot4] %s Price=$%,.2f Ratio=%.2fx Regime=%s", SYMBOL, price, ratio, regime)
        if ratio>=SPIKE_MULT:
            side="BUY" if regime in ("bull","ranging") else "SELL"
            log.info("[Bot4] %s %s @ $%,.2f spike %.1fx", "LIVE" if is_live else "PAPER", side, price, ratio)
        else: log.info("[Bot4] No spike ratio=%.2fx", ratio)
    except ImportError: log.warning("[Bot4] ccxt not available.")
    except Exception as e: log.error("[Bot4] Error: %s", e, exc_info=True)
