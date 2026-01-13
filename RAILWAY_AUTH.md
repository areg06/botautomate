# Railway Telegram Authentication Guide

Railway doesn't have a web shell, so here are the best ways to authenticate Telegram:

## Method 1: Upload Session File from Local (Easiest) ⭐

If you've already authenticated on your local machine:

1. **Authenticate locally first** (if not done):
   ```bash
   python3 trading_bot.py
   # Enter phone number and code
   ```

2. **Copy the session file**:
   - The session file is: `trading_bot_session.session`
   - Also copy: `trading_bot_session.session-journal` (if it exists)

3. **Upload to Railway using Railway CLI**:
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli
   # or: brew install railway
   
   # Login
   railway login
   
   # Link your project
   railway link
   
   # Upload session file
   railway run --service your-service-name cp trading_bot_session.session /app/trading_bot_session.session
   ```

4. **Or use Railway's file upload** (if available in dashboard):
   - Go to your service → Settings → Volumes
   - Mount a volume and upload the session file

## Method 2: Use Railway CLI Shell ⭐ Recommended

1. **Install Railway CLI** (if not done):
   ```bash
   npm i -g @railway/cli
   # or: brew install railway
   ```

2. **Login and link**:
   ```bash
   railway login          # Opens browser for auth
   cd /path/to/autmomate # Navigate to your project
   railway link           # Select your Railway project
   ```

3. **Open shell with Railway environment**:
   ```bash
   railway shell
   ```
   This connects you to your Railway service with all environment variables loaded.

4. **Run bot interactively**:
   ```bash
   python3 trading_bot.py
   ```
   When prompted:
   - Enter your phone number (with country code, e.g., `+1234567890`)
   - Enter the verification code from Telegram
   - Enter 2FA password if you have it enabled

5. **Session will be saved automatically** in Railway's file system

6. **Exit and verify**:
   - Press `Ctrl+C` to stop the bot
   - Type `exit` to leave Railway shell
   - Check Railway dashboard logs - bot should now be running!

See `RAILWAY_SHELL_AUTH.md` for detailed step-by-step guide.

## Method 3: Use Local Session File Directly

The easiest approach - authenticate locally and upload the session file:

1. **On your local machine**, make sure you have the session file:
   ```bash
   ls -la trading_bot_session.session
   ```

2. **Use Railway CLI to copy it**:
   ```bash
   railway link
   railway run cp /local/path/trading_bot_session.session /app/
   ```

## Method 4: Create Auth Script (Advanced)

Create a separate authentication script that you run once, then the main bot uses the session.
