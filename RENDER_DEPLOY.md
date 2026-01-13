# Render.com Deployment Guide

## Quick Setup (5 minutes)

### Step 1: Prepare Your Repository

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

### Step 2: Deploy on Render

1. **Sign up/Login**:
   - Go to [render.com](https://render.com)
   - Sign up or log in (you can use GitHub to sign in)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account if not already connected
   - Select your repository (`autmomate`)

3. **Configure Service**:
   - **Name**: `trading-bot` (or any name you like)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `./` if needed)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 trading_bot.py`
   - **Plan**: Select "Free" (750 hours/month)

4. **Add Environment Variables**:
   - Scroll down to "Environment Variables"
   - Click "Add Environment Variable" for each:
     ```
     BINANCE_API_KEY=your_binance_api_key
     BINANCE_API_SECRET=your_binance_api_secret
     TELEGRAM_APP_ID=your_telegram_app_id
     TELEGRAM_API_HASH=your_telegram_api_hash
     TELEGRAM_CHANNEL_ID=your_channel_id
     DRY_RUN=true
     ```
   - **Important**: Set `DRY_RUN=true` initially for testing!
   - **Note**: `PORT` is automatically set by Render (don't need to set it manually)

5. **Deploy**:
   - Click "Create Web Service"
   - Render will start building and deploying
   - Watch the logs for progress

### Step 3: First-Time Telegram Authentication

1. **Wait for deployment to complete**
   - Check the "Logs" tab
   - You'll see: "Please enter your phone (or bot token):"

2. **Use Render Shell** (if available):
   - Go to your service → "Shell" tab
   - Run: `python3 trading_bot.py`
   - Enter your phone number and verification code

3. **Or authenticate locally and upload session**:
   - Run bot locally: `python3 trading_bot.py`
   - Authenticate Telegram
   - Upload `trading_bot_session.session` to Render
   - Go to "Environment" → "Secret Files" (if available)
   - Or use Render CLI to upload

### Step 4: Prevent Sleep (Important!)

**Render free tier sleeps after 15 minutes of inactivity.**

To keep it awake:

1. **Option A: Use UptimeRobot (Recommended - Free)**:
   - Sign up at [uptimerobot.com](https://uptimerobot.com)
   - Add a new monitor
   - Monitor type: "HTTP(s)"
   - URL: Your Render service URL (e.g., `https://trading-bot.onrender.com`)
   - Monitoring interval: 5 minutes
   - This will ping your service every 5 minutes to keep it awake

2. **Option B: Use cron-job.org (Free)**:
   - Sign up at [cron-job.org](https://cron-job.org)
   - Create a new cron job
   - URL: Your Render service URL
   - Schedule: Every 5 minutes
   - Method: GET

3. **Option C: Upgrade to Paid Plan**:
   - Render paid plans ($7/month) don't sleep
   - Better for production use

## Render Features

- **Free Tier**: 750 hours/month (enough for continuous running if kept awake)
- **Auto-deploy**: Deploys on every GitHub push
- **Logs**: Real-time log viewing
- **Environment Variables**: Secure storage
- **Auto-restart**: Restarts on crash
- **Public URL**: Get a public URL for your service

## Environment Variables Reference

Set these in Render dashboard → Your service → Environment:

```
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
TELEGRAM_APP_ID=your_telegram_app_id
TELEGRAM_API_HASH=your_telegram_api_hash
TELEGRAM_CHANNEL_ID=your_channel_id
DRY_RUN=true          # Set to false for live trading
# PORT is automatically set by Render - no need to specify
```

## Troubleshooting

### Bot won't start
- Check logs for errors
- Verify all environment variables are set
- Ensure Python version is 3.11+ (Render auto-detects)

### Telegram authentication issues
- Use Render Shell to authenticate interactively
- Or authenticate locally and upload session file
- Check that session file persists between restarts

### Bot goes to sleep
- Set up UptimeRobot to ping every 5 minutes
- Or upgrade to paid plan
- Check logs to see when it last received a request

### Connection errors
- Render allows outbound connections (unlike PythonAnywhere free)
- If you see connection errors, check Telegram API credentials
- Verify network connectivity in logs

### Session file not persisting
- Render has persistent storage
- Session files should persist between restarts
- If not, check file permissions and paths

## Monitoring Your Bot

1. **View Logs**:
   - Go to your service → "Logs" tab
   - See real-time logs
   - Look for "Telegram client initialized successfully"
   - Watch for signal detection messages

2. **Check Status**:
   - Service should show "Live" status
   - Green indicator means it's running
   - Visit your public URL to see status page

3. **Test Signal Detection**:
   - Send a test signal to your Telegram channel
   - Check logs for "Received potential signal message"
   - Verify parsing and execution (in DRY_RUN mode)

## Switching to Live Trading

When ready to execute real trades:

1. **Go to Environment Variables**
2. **Change `DRY_RUN=false`**
3. **Save changes**
4. **Render will automatically redeploy**
5. **Monitor logs carefully for first trades**

## Cost Management

- **Free tier**: 750 hours/month
- **If kept awake**: Uses ~730 hours/month
- **Upgrade needed**: Only if you want guaranteed uptime (no sleep)
- **Paid plan**: $7/month for always-on service

## Next Steps

1. ✅ Deploy to Render
2. ✅ Set environment variables
3. ✅ Authenticate Telegram
4. ✅ Set up UptimeRobot to prevent sleep
5. ✅ Test with DRY_RUN=true
6. ✅ Monitor logs for signal detection
7. ⚠️ Switch to DRY_RUN=false when confident
