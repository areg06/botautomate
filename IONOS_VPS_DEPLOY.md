# IONOS VPS Deployment Guide

## Prerequisites

1. **IONOS VPS Account**
   - Sign up at [ionos.com](https://www.ionos.com)
   - Create a VPS (Virtual Private Server)
   - Choose Linux OS (Ubuntu 22.04 recommended)

2. **SSH Access**
   - You'll receive SSH credentials from IONOS
   - IP address, username, and password (or SSH key)

## Step 1: Connect to Your VPS

### Using Windows:
- Use **PuTTY** (download from [putty.org](https://www.putty.org/))
- Or use **Windows Terminal** / **PowerShell**:
  ```powershell
  ssh root@your-vps-ip
  ```

### Using Mac/Linux:
```bash
ssh root@your-vps-ip
```

Enter your password when prompted.

## Step 2: Update System

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y python3 python3-pip python3-venv git curl
```

## Step 3: Create User (Optional but Recommended)

```bash
# Create a new user (replace 'trader' with your preferred username)
sudo adduser trader

# Add user to sudo group
sudo usermod -aG sudo trader

# Switch to new user
su - trader
```

## Step 4: Clone or Upload Your Project

### Option A: Clone from GitHub (Recommended)

```bash
# Install Git if not already installed
sudo apt install -y git

# Clone your repository
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git automomate
cd automomate
```

### Option B: Upload Files via SCP

From your local machine:
```bash
# Windows (PowerShell)
scp -r C:\path\to\autmomate root@your-vps-ip:/root/

# Mac/Linux
scp -r ~/autmomate root@your-vps-ip:/root/
```

Then on VPS:
```bash
cd ~/autmomate
```

### Option C: Upload via SFTP

Use FileZilla or WinSCP:
- Host: `your-vps-ip`
- Username: `root` (or your username)
- Password: Your VPS password
- Port: `22`

Upload the project folder to `/root/autmomate` or `/home/trader/autmomate`

## Step 5: Set Up Python Environment

```bash
# Navigate to project directory
cd ~/autmomate

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## Step 6: Configure Environment Variables

```bash
# Create .env file
nano .env
```

Add your credentials:
```
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
TELEGRAM_APP_ID=your_telegram_app_id_here
TELEGRAM_API_HASH=your_telegram_api_hash_here
TELEGRAM_CHANNEL_ID=your_channel_id_here
DRY_RUN=true
PORT=8000
```

Save and exit:
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter` to save

## Step 7: First-Time Telegram Authentication

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the bot
python3 trading_bot.py
```

When prompted:
1. Enter your phone number (with country code)
2. Enter verification code from Telegram
3. Enter 2FA password if enabled

Press `Ctrl + C` to stop after authentication.

## Step 8: Create Systemd Service (Auto-Start on Boot)

```bash
# Create service file
sudo nano /etc/systemd/system/trading-bot.service
```

Add this content (adjust paths as needed):
```ini
[Unit]
Description=Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/autmomate
Environment="PATH=/root/autmomate/venv/bin:/usr/bin"
ExecStart=/root/autmomate/venv/bin/python3 /root/autmomate/trading_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**If using a different user/path, adjust:**
- `User=trader` (if using 'trader' user)
- `WorkingDirectory=/home/trader/autmomate`
- `Environment="PATH=/home/trader/autmomate/venv/bin:/usr/bin"`
- `ExecStart=/home/trader/autmomate/venv/bin/python3 /home/trader/autmomate/trading_bot.py`

Save and exit (`Ctrl + X`, `Y`, `Enter`)

## Step 9: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (starts on boot)
sudo systemctl enable trading-bot

# Start service
sudo systemctl start trading-bot

# Check status
sudo systemctl status trading-bot
```

## Step 10: Configure Firewall (If Needed)

```bash
# Check if UFW is installed
sudo ufw status

# If not installed, install it
sudo apt install -y ufw

# Allow SSH (important - do this first!)
sudo ufw allow 22/tcp

# Allow web server port (if you want to access web interface)
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## Step 11: Access Web Interface

If you want to access the web interface from outside:

1. **Check your VPS IP** (you should already have this)

2. **Access via browser:**
   ```
   http://your-vps-ip:8000
   ```

3. **If using IONOS firewall, allow port 8000:**
   - Log into IONOS control panel
   - Go to Firewall settings
   - Add rule: Allow TCP port 8000

## Managing the Service

### View Logs
```bash
# View live logs
sudo journalctl -u trading-bot -f

# View last 100 lines
sudo journalctl -u trading-bot -n 100

# View logs since today
sudo journalctl -u trading-bot --since today
```

### Stop Service
```bash
sudo systemctl stop trading-bot
```

### Start Service
```bash
sudo systemctl start trading-bot
```

### Restart Service
```bash
sudo systemctl restart trading-bot
```

### Disable Auto-Start
```bash
sudo systemctl disable trading-bot
```

### Check Status
```bash
sudo systemctl status trading-bot
```

## Updating the Bot

```bash
# Navigate to project
cd ~/autmomate

# If using Git, pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies (if requirements.txt changed)
pip install -r requirements.txt

# Restart service
sudo systemctl restart trading-bot
```

## Troubleshooting

### Service won't start
```bash
# Check service status
sudo systemctl status trading-bot

# Check logs for errors
sudo journalctl -u trading-bot -n 50

# Verify paths in service file
cat /etc/systemd/system/trading-bot.service

# Test running manually
cd ~/autmomate
source venv/bin/activate
python3 trading_bot.py
```

### Permission errors
```bash
# Make sure service user has access
sudo chown -R root:root ~/autmomate
# Or if using different user:
sudo chown -R trader:trader /home/trader/autmomate
```

### Port already in use
```bash
# Check what's using the port
sudo lsof -i :8000

# Kill the process or change PORT in .env
```

### Can't access web interface
```bash
# Check if service is running
sudo systemctl status trading-bot

# Check if port is listening
sudo netstat -tlnp | grep 8000

# Check firewall
sudo ufw status

# Test locally on VPS
curl http://localhost:8000
```

### Telegram authentication issues
```bash
# Stop service
sudo systemctl stop trading-bot

# Run manually to re-authenticate
cd ~/autmomate
source venv/bin/activate
python3 trading_bot.py

# After authentication, restart service
sudo systemctl start trading-bot
```

## Security Best Practices

1. **Use SSH Keys instead of passwords:**
   ```bash
   # On your local machine, generate key
   ssh-keygen -t rsa -b 4096
   
   # Copy to VPS
   ssh-copy-id root@your-vps-ip
   ```

2. **Disable root login (after creating user):**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PermitRootLogin no
   sudo systemctl restart sshd
   ```

3. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Use strong passwords for .env file:**
   ```bash
   # Restrict .env file permissions
   chmod 600 ~/autmomate/.env
   ```

## Monitoring

### Check if bot is running
```bash
ps aux | grep trading_bot
```

### Monitor resource usage
```bash
# CPU and memory
top

# Or use htop (install: sudo apt install htop)
htop
```

### Check disk space
```bash
df -h
```

## Backup

### Backup session file
```bash
# Create backup directory
mkdir -p ~/backups

# Backup session file
cp ~/autmomate/trading_bot_session.session ~/backups/session_$(date +%Y%m%d).session
```

### Backup entire project
```bash
tar -czf ~/backups/autmomate_$(date +%Y%m%d).tar.gz ~/autmomate
```

## Quick Reference Commands

```bash
# Start bot
sudo systemctl start trading-bot

# Stop bot
sudo systemctl stop trading-bot

# Restart bot
sudo systemctl restart trading-bot

# View logs
sudo journalctl -u trading-bot -f

# Check status
sudo systemctl status trading-bot

# Edit .env
nano ~/autmomate/.env

# Update and restart
cd ~/autmomate && git pull && sudo systemctl restart trading-bot
```

## IONOS-Specific Notes

1. **IONOS Control Panel:**
   - Access via [ionos.com](https://www.ionos.com)
   - Manage VPS, firewall, and networking

2. **Firewall Rules:**
   - Configure in IONOS control panel
   - Or use UFW on the server

3. **IP Address:**
   - Static IP is usually provided
   - Check in IONOS control panel

4. **Backup:**
   - IONOS may offer snapshot/backup features
   - Use control panel to configure

5. **Resource Monitoring:**
   - Monitor CPU, RAM, and bandwidth in IONOS dashboard
   - Upgrade plan if needed

## Next Steps

1. ✅ Deploy bot to IONOS VPS
2. ✅ Set up systemd service
3. ✅ Configure firewall
4. ✅ Test web interface
5. ✅ Monitor logs
6. ✅ Set up backups
7. ⚠️ Switch DRY_RUN=false when ready for live trading
