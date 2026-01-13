# Telegram Signal Trading Bot

Automated trading bot that monitors Telegram channels for trading signals and executes trades on Binance Futures.

## Features

- 🔍 Monitors Telegram channels for trading signals
- 📊 Parses signals with regex (direction, symbol, leverage, entry, targets)
- 💹 Executes trades on Binance Futures via CCXT
- 🎯 Automatically sets leverage and places take profit orders
- 🛡️ Dry run mode for safe testing
- ☁️ Ready for cloud deployment (Railway, Render, etc.)

## Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Run the bot**:
```bash
python3 trading_bot.py
```

## Deployment

See [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) for Railway.app deployment instructions.

## Environment Variables

- `BINANCE_API_KEY` - Your Binance Futures API key
- `BINANCE_API_SECRET` - Your Binance Futures API secret
- `TELEGRAM_APP_ID` - Telegram API ID (from https://my.telegram.org/apps)
- `TELEGRAM_API_HASH` - Telegram API hash
- `TELEGRAM_CHANNEL_ID` - Channel ID to monitor
- `DRY_RUN` - Set to `true` for testing (default: `true`)

## Signal Format

The bot expects signals in this format:

```
🟢 Long
Name: ETH/USDT
Margin mode: Cross (100.0X)
↪️ Entry price(USDT):
3127.20
Targets(USDT):
1) 3158.47
2) 3189.74
3) 3220.01
```

## License

MIT
