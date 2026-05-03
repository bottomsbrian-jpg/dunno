# NEXUS Trading Bot

A multi-bot algorithmic trading system with 10 strategy bots coordinated by a leader bot.

## Bots
- **Leader Bot**: Fetches market data, determines regime (bull/bear/ranging/volatile)
- **Bot 1**: RSI Momentum (BTC 1H)
- **Bot 2**: EMA Crossover (ETH 1H)
- **Bot 3**: Bollinger Band Mean Reversion (BTC 4H)
- **Bot 4**: Volume Spike Detection (BTC 1H)
- **Bot 5**: MACD Signal (ETH 4H)
- **Bot 6**: Support/Resistance Breakout (BTC 1H)
- **Bot 7**: ADX Trend Following (BTC 4H)
- **Bot 8**: Multi-Timeframe Confirmation (BTC)
- **Bot 9**: ETH/BTC Divergence Scanner
- **Bot 10**: Portfolio Risk Monitor

## Setup
1. Add your API keys as Railway environment variables
2. Set NEXUS_TRADING_MODE=paper to run in paper mode (no real trades)
3. Set NEXUS_TRADING_MODE=live only when ready for real trading

## Environment Variables
See .env.template for all required variables.
