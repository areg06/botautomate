# Free Hosting Guide for Trading Bot

## Best Free Hosting Options (2024-2025)

### 1. **Railway.app** ⭐ Recommended
- **Free Tier**: $5 credit/month (enough for small bots)
- **Pros**: Easy deployment, persistent storage, good for long-running processes
- **Setup**:
  1. Sign up at [railway.app](https://railway.app)
  2. Connect your GitHub repo
  3. Create new project → Deploy from GitHub
  4. Add environment variables in Railway dashboard
  5. Set start command: `python3 trading_bot.py`

### 2. **Render.com**
- **Free Tier**: 750 hours/month (enough for continuous running)
- **Pros**: Free tier available, easy setup
- **Cons**: Spins down after 15 min inactivity (use uptime monitor)
- **Setup**:
  1. Sign up at [render.com](https://render.com)
  2. Create new Web Service
  3. Connect GitHub repo
  4. Build command: `pip install -r requirements.txt`
  5. Start command: `python3 trading_bot.py`
  6. Add environment variables in dashboard

### 3. **Fly.io**
- **Free Tier**: 3 shared VMs, 3GB storage
- **Pros**: Good performance, persistent storage
- **Setup**:
  1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
  2. Sign up: `fly auth signup`
  3. Create app: `fly launch`
  4. Deploy: `fly deploy`

### 4. **PythonAnywhere**
- **Free Tier**: 1 always-on task
- **Pros**: Specifically for Python, easy setup
- **Cons**: Limited resources
- **Setup**:
  1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
  2. Upload files via Files tab
  3. Create a Bash console
  4. Install dependencies: `pip3.10 install --user -r requirements.txt`
  5. Run: `python3.10 trading_bot.py`

### 5. **Oracle Cloud Always Free** ⭐ Best for Long-term
- **Free Tier**: 2 VMs with 1GB RAM each (permanent free tier)
- **Pros**: Actual VPS, full control, never expires
- **Cons**: Requires credit card (no charges if within free tier)
- **Setup**:
  1. Sign up at [cloud.oracle.com](https://cloud.oracle.com)
  2. Create Always Free VM (Ubuntu)
  3. SSH into VM
  4. Install Python and dependencies
  5. Use systemd service (see below)

## Quick Setup Instructions

### For Railway/Render/Fly.io:

1. **Create a Procfile** (for Railway/Render):
```
worker: python3 trading_bot.py
```

2. **Add runtime.txt** (optional, for Python version):
```
python-3.11.0
```

3. **Important Notes**:
   - Session files persist on Railway and Fly.io
   - Render may need uptime monitoring to prevent sleep
   - All platforms support environment variables

### For Oracle Cloud VPS (Most Reliable):

1. **SSH into your VM**:
```bash
ssh ubuntu@your-vm-ip
```

2. **Install dependencies**:
```bash
sudo apt update
sudo apt install python3-pip git -y
git clone your-repo-url
cd automomate
pip3 install -r requirements.txt
```

3. **Create systemd service** (runs on boot):
```bash
sudo nano /etc/systemd/system/trading-bot.service
```

Add this content:
```ini
[Unit]
Description=Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/autmomate
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /home/ubuntu/autmomate/trading_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. **Enable and start**:
```bash
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

## Environment Variables Setup

For all platforms, set these in their dashboard/CLI:

```
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
TELEGRAM_APP_ID=your_app_id
TELEGRAM_API_HASH=your_hash
TELEGRAM_CHANNEL_ID=your_channel_id
DRY_RUN=true  # Set to false for live trading
```

## First-Time Telegram Authentication

**Important**: You need to authenticate Telegram interactively the first time:

1. **Option A**: Run locally first, then upload the `.session` file
   - Run bot locally: `python3 trading_bot.py`
   - Complete authentication
   - Upload `trading_bot_session.session` to your hosting platform

2. **Option B**: Use SSH/console on your hosting platform
   - Connect via SSH (VPS) or use web console (Railway/Render)
   - Run bot once interactively
   - Session file will be saved

## Monitoring & Logs

- **Railway**: Built-in logs dashboard
- **Render**: Logs tab in dashboard
- **Fly.io**: `fly logs`
- **VPS**: `journalctl -u trading-bot -f`

## Keep-Alive for Render (Prevent Sleep)

If using Render, add an uptime monitor:
- Use [UptimeRobot](https://uptimerobot.com) (free)
- Ping your Render service every 5 minutes
- Or use a simple health check endpoint (see code updates)

## Recommended Choice

**For beginners**: Railway.app (easiest setup)
**For reliability**: Oracle Cloud Always Free VPS (permanent, full control)
**For quick testing**: Render.com (fastest to deploy)
