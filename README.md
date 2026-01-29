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

### VPS (e.g. IONOS, EVPS) – Quick reference

**Connect**
```bash
ssh root@YOUR_VPS_IP
# or: ssh user@YOUR_VPS_IP
```

**One-time setup**
```bash
cd /root   # or your home
git clone YOUR_REPO_URL botautomate
cd botautomate
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
nano .env   # fill BINANCE_*, TELEGRAM_*, TELEGRAM_CHANNEL_ID, DRY_RUN, etc.
```

**First-time Telegram auth (interactive)**
```bash
cd /root/botautomate && source venv/bin/activate && python3 trading_bot.py
# Enter phone/QR, then Ctrl+C once "Bot is running" appears. Session is saved.
```

**Run bot (foreground)**
```bash
cd /root/botautomate && source venv/bin/activate && python3 trading_bot.py
```

**Run dashboard (port 4000)**
```bash
cd /root/botautomate && source venv/bin/activate && python3 dashboard_server.py
# Or: DASHBOARD_PORT=4000 python3 dashboard_server.py
```

**Run both with systemd**

On the VPS, create the service files by running the script (from the project folder):
```bash
cd /root/botautomate
bash vps-create-services.sh
```
Then start and enable:
```bash
sudo systemctl start trading-bot trading-dashboard
sudo systemctl enable trading-bot trading-dashboard
```

Or create the files manually. `/etc/systemd/system/trading-bot.service`:
```ini
[Unit]
Description=Telegram Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/botautomate
Environment="PATH=/root/botautomate/venv/bin"
ExecStart=/root/botautomate/venv/bin/python3 trading_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/trading-dashboard.service`:
```ini
[Unit]
Description=Trading Bot Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/botautomate
Environment="PATH=/root/botautomate/venv/bin"
Environment="DASHBOARD_PORT=4000"
ExecStart=/root/botautomate/venv/bin/python3 dashboard_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Systemd commands**
```bash
sudo systemctl daemon-reload
sudo systemctl start trading-bot
sudo systemctl start trading-dashboard
sudo systemctl enable trading-bot
sudo systemctl enable trading-dashboard
sudo systemctl status trading-bot
sudo systemctl status trading-dashboard
sudo journalctl -u trading-bot -f
sudo journalctl -u trading-dashboard -f
sudo systemctl stop trading-bot
sudo systemctl stop trading-dashboard
```

**Useful VPS checks**
```bash
# Ports in use
ss -tlnp | grep -E '4000|8080'
# Or: netstat -tlnp | grep -E '4000|8080'

# Kill process on port 4000
fuser -k 4000/tcp

# Test dashboard from VPS
curl -s http://127.0.0.1:4000/ | head -20
```

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
