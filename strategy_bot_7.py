import logging
log = logging.getLogger("nexus.bot7")
SYMBOL = "BTC/USDT"
PERIOD=14; ADX_STRONG=25

def _adx(ohlcv,period):
    if len(ohlcv)<period+1: return 0,0,0
    trs,dp,dm=[],[],[]
    for i in range(1,len(ohlcv)):
        h,l,pc=ohlcv[i][2],ohlcv[i][3],ohlcv[i-1][4]
        trs.append(max(h-l,abs(h-pc),abs(l-pc)))
        dp.append(max(h-ohlcv[i-1][2],0) if (h-ohlcv[i-1][2])>(ohlcv[i-1][3]-l) else 0)
        dm.append(max(ohlcv[i-1][3]-l,0) if (ohlcv[i-1][3]-l)>(h-ohlcv[i-1][2]) else 0)
    atr=sum(trs[-period:])/period
    if atr==0: return 0,0,0
    dip=(sum(dp[-period:])/period)/atr*100; dim=(sum(dm[-period:])/period)/atr*100
    return abs(dip-dim)/(dip+dim)*100 if (dip+dim) else 0,dip,dim

def run(is_live=False):
    log.info("[Bot7] ADX Trend start.")
    try:
        import ccxt
        ex=ccxt.binance({"enableRateLimit":True})
        ohlcv=ex.fetch_ohlcv(SYMBOL,"4h",limit=PERIOD+10)
        adx,dip,dim=_adx(ohlcv,PERIOD); price=ohlcv[-1][4]
        log.info("[Bot7] %s Price=$%,.2f ADX=%.1f +DI=%.1f -DI=%.1f",SYMBOL,price,adx,dip,dim)
        if adx>=ADX_STRONG:
            side="BUY" if dip>dim else "SELL"
            log.info("[Bot7] %s %s @ $%,.2f ADX=%.1f","LIVE" if is_live else "PAPER",side,price,adx)
        else: log.info("[Bot7] Weak trend ADX=%.1f",adx)
    except ImportError: log.warning("[Bot7] ccxt not available.")
    except Exception as e: log.error("[Bot7] Error: %s",e,exc_info=True)
