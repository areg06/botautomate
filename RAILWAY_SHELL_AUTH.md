# Railway Shell Authentication Guide

## Quick Steps to Authenticate via Railway Shell

### Prerequisites
✅ Railway CLI installed (`npm i -g @railway/cli`)
✅ Session file exists locally (`trading_bot_session.session`)

### Step 1: Login to Railway
```bash
railway login
```
- This will open your browser for authentication
- Authorize Railway to access your account

### Step 2: Navigate to Project Directory
```bash
cd /Users/aregkhachatryan/Desktop/cursor/autmomate
```

### Step 3: Link Your Railway Project
```bash
railway link
```
- Select your project from the list
- If you have multiple projects, choose the one where your bot is deployed

### Step 4: Open Railway Shell
```bash
railway shell
```
- This opens an interactive shell with Railway's environment variables loaded
- You're now connected to your Railway service

### Step 5: Upload Session File

**Option A: Copy from local (if Railway supports file operations)**
```bash
# In Railway shell, you can try to copy the file
# But Railway shell might not have direct file upload
# So we'll use Option B instead
```

**Option B: Authenticate directly in Railway shell (Recommended)**
```bash
# Make sure you're in the Railway shell
# Then run:
python3 trading_bot.py
```

When prompted:
1. Enter your phone number (with country code, e.g., `+1234567890`)
2. Enter the verification code sent to your Telegram
3. If you have 2FA, enter your password

The session file will be saved automatically in Railway's file system.

### Step 6: Exit and Verify
```bash
# Press Ctrl+C to stop the bot
# Type 'exit' to leave Railway shell
exit
```

### Step 7: Check Railway Logs
- Go to Railway dashboard
- Check "View Logs" 
- You should see "Telegram client initialized successfully"
- Bot should now be running and monitoring your channel

## Troubleshooting

### If `railway shell` doesn't work:
- Make sure you're linked: `railway link`
- Check you're in the right directory
- Try: `railway status` to verify connection

### If authentication fails:
- Make sure environment variables are set in Railway dashboard
- Check that `TELEGRAM_APP_ID` and `TELEGRAM_API_HASH` are correct
- Try running `python3 auth_telegram.py` in Railway shell instead

### If session file doesn't persist:
- Railway should persist files in the working directory
- Check logs to see where the session file is being saved
- The bot uses: `trading_bot_session.session` in the current directory
