# Quick Deploy Guide

## Fastest Option: Railway.app (5 minutes)

1. **Sign up**: Go to [railway.app](https://railway.app) and sign up with GitHub

2. **Deploy**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect Python

3. **Configure**:
   - Go to "Variables" tab
   - Add all environment variables from `.env`
   - Set `DRY_RUN=true` for testing

4. **First-time Telegram Auth**:
   - Go to "Deployments" → Click on latest deployment → "View Logs"
   - You'll see "Please enter your phone"
   - Click "Open Shell" in Railway dashboard
   - Run: `python3 trading_bot.py`
   - Enter phone number and code interactively
   - Session file will be saved automatically

5. **Done!** Your bot is now running 24/7

## Alternative: Render.com (Free but may sleep)

1. Sign up at [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python3 trading_bot.py`
5. Add environment variables
6. Deploy

**Note**: Render free tier sleeps after 15 min. Use [UptimeRobot](https://uptimerobot.com) to ping it every 5 minutes.

## Best Long-term: Oracle Cloud (Free Forever VPS)

1. Sign up at [cloud.oracle.com](https://cloud.oracle.com) (needs credit card, but free tier is truly free)
2. Create Always Free VM (Ubuntu 22.04)
3. SSH into VM
4. Run these commands:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Git
sudo apt install python3-pip python3-venv git -y

# Clone your repo (or upload files)
git clone YOUR_REPO_URL
cd automomate

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# First-time Telegram auth
python3 trading_bot.py
# (Enter phone number and code)

# Create systemd service for auto-start
sudo nano /etc/systemd/system/trading-bot.service
```

Paste this in the service file:
```ini
[Unit]
Description=Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/autmomate
Environment="PATH=/home/ubuntu/autmomate/venv/bin:/usr/bin"
ExecStart=/home/ubuntu/autmomate/venv/bin/python3 /home/ubuntu/autmomate/trading_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

Your bot will now run automatically on boot and restart if it crashes!
