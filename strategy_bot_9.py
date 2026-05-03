import logging
log = logging.getLogger("nexus.bot9")
RATIO_HIGH=0.075; RATIO_LOW=0.045

def run(is_live=False):
    log.info("[Bot9] Divergence start.")
    try:
        import ccxt
        ex=ccxt.binance({"enableRateLimit":True})
        btc=ex.fetch_ticker("BTC/USDT"); eth=ex.fetch_ticker("ETH/USDT")
        bp=float(btc["last"]); ep=float(eth["last"])
        bc=float(btc.get("percentage") or 0); ec=float(eth.get("percentage") or 0)
        ratio=ep/bp if bp else 0; div=ec-bc
        log.info("[Bot9] BTC=$%,.2f(%+.2f%%) ETH=$%,.2f(%+.2f%%) Div=%+.2f%%",bp,bc,ep,ec,div)
        if div>4 and ratio<RATIO_HIGH: log.info("[Bot9] %s BUY ETH @ $%,.2f div=%.1f%%","LIVE" if is_live else "PAPER",ep,div)
        elif div<-4 and ratio>RATIO_LOW: log.info("[Bot9] %s BUY BTC @ $%,.2f div=%.1f%%","LIVE" if is_live else "PAPER",bp,abs(div))
        else: log.info("[Bot9] No divergence div=%+.2f%%",div)
    except ImportError: log.warning("[Bot9] ccxt not available.")
    except Exception as e: log.error("[Bot9] Error: %s",e,exc_info=True)
