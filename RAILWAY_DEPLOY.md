# Railway.app Deployment Guide

## Step-by-Step Setup

### Prerequisites
- GitHub account
- Railway.app account (sign up at [railway.app](https://railway.app))

### Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit - Trading bot"
```

2. **Push to GitHub**:
   - Create a new repository on GitHub
   - Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway

1. **Sign up/Login**:
   - Go to [railway.app](https://railway.app)
   - Click "Login" → "Login with GitHub"
   - Authorize Railway to access your GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository (`autmomate` or whatever you named it)
   - Railway will automatically detect Python

3. **Configure Environment Variables**:
   - Click on your project
   - Go to "Variables" tab
   - Add each variable (click "New Variable" for each):
     ```
     BINANCE_API_KEY=your_binance_api_key
     BINANCE_API_SECRET=your_binance_api_secret
     TELEGRAM_APP_ID=your_telegram_app_id
     TELEGRAM_API_HASH=your_telegram_api_hash
     TELEGRAM_CHANNEL_ID=your_channel_id
     DRY_RUN=true
     ```
   - **Important**: Set `DRY_RUN=true` initially for testing!

4. **Configure Service**:
   - Go to "Settings" tab
   - Under "Start Command", ensure it's: `python3 trading_bot.py`
   - Railway should auto-detect this from the Procfile

5. **First-Time Telegram Authentication**:
   - Go to "Deployments" tab
   - Click on the latest deployment
   - Click "View Logs"
   - You'll see: "Please enter your phone (or bot token):"
   - Click "Open Shell" button (top right of logs)
   - In the shell, run: `python3 trading_bot.py`
   - Enter your phone number (with country code, e.g., +1234567890)
   - Enter the verification code sent to your Telegram
   - If you have 2FA, enter your password
   - The session file will be saved automatically
   - Close the shell and the bot will restart with the saved session

6. **Monitor Your Bot**:
   - Go to "Deployments" → "View Logs" to see real-time logs
   - Your bot will automatically restart if it crashes
   - Check logs for signal detection and trade execution

### Step 3: Verify It's Working

1. **Check Logs**:
   - Should see: "Telegram client initialized successfully"
   - Should see: "Started listening to channel [YOUR_CHANNEL_ID]"
   - Should see: "Bot is running. Press Ctrl+C to stop."

2. **Test Signal Detection**:
   - Send a test signal to your Telegram channel
   - Check logs to see if it's detected and parsed

3. **Switch to Live Mode** (when ready):
   - Go to "Variables" tab
   - Change `DRY_RUN=false`
   - Railway will automatically redeploy

## Railway Features

- **Automatic Deploys**: Every push to GitHub triggers a new deployment
- **Persistent Storage**: Session files are saved between restarts
- **Logs**: Real-time log viewing in dashboard
- **Environment Variables**: Secure storage of API keys
- **Auto-restart**: Bot restarts automatically if it crashes
- **Free Tier**: $5 credit/month (usually enough for 1 bot)

## Troubleshooting

### Python version installation error
If you see: `mise ERROR Failed to install core:python@3.11.0`
- **Solution 1**: Update `runtime.txt` to `python-3.12` (already done)
- **Solution 2**: Remove `runtime.txt` entirely and let Railway auto-detect Python
- **Solution 3**: Add environment variable `RAILPACK_PYTHON_VERSION=3.12` in Railway dashboard

### Bot won't start
- Check logs for errors
- Verify all environment variables are set
- Ensure Python version is compatible (3.11+)

### Telegram authentication issues
- Use the web shell to authenticate interactively
- Make sure session file is being saved (check logs)
- If session expires, re-authenticate via shell

### Bot not detecting signals
- Verify `TELEGRAM_CHANNEL_ID` is correct
- Check that you're subscribed to the channel
- Look for "Received potential signal message" in logs

### Out of credits
- Railway free tier: $5/month
- Upgrade to Hobby plan ($5/month) for more resources
- Or switch to Oracle Cloud (truly free)

## Cost Management

- Free tier: $5 credit/month
- Small bot uses ~$1-2/month typically
- Monitor usage in Railway dashboard
- Set up billing alerts if needed

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Authenticate Telegram
3. ✅ Test with DRY_RUN=true
4. ✅ Monitor logs for signal detection
5. ⚠️ Switch to DRY_RUN=false when confident
6. ✅ Monitor first live trades carefully
