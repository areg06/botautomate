# How to Get New Telegram API Credentials

If you're having issues receiving verification codes, you can create a new Telegram app with fresh API credentials.

## Step-by-Step Guide

### Step 1: Go to Telegram API Development Platform

1. Open your web browser
2. Go to: **https://my.telegram.org/apps**
3. Log in with your phone number (the same one you're using for the bot)

### Step 2: Create a New Application

1. If you already have an app, you can:
   - **Option A**: Delete the old app and create a new one
   - **Option B**: Create a new app (you can have multiple)

2. To create a new app:
   - Click **"Create new application"** or **"API development tools"**
   - Fill in the form:
     - **App title**: `Trading Bot` (or any name)
     - **Short name**: `tradingbot` (or any short name)
     - **URL**: Leave empty or put `https://example.com`
     - **Platform**: Choose `Other`
     - **Description**: `Automated trading bot` (optional)

3. Click **"Create application"**

### Step 3: Get Your New Credentials

After creating the app, you'll see:
- **api_id**: A number (e.g., `12345678`)
- **api_hash**: A long string (e.g., `abcdef1234567890abcdef1234567890`)

**Important**: Copy these immediately - you won't be able to see the api_hash again!

### Step 4: Update Your .env File

1. Open your `.env` file:
   ```bash
   nano .env
   # or
   notepad .env  # Windows
   ```

2. Update these two lines with your NEW credentials:
   ```
   TELEGRAM_APP_ID=your_new_api_id_here
   TELEGRAM_API_HASH=your_new_api_hash_here
   ```

3. Save the file

### Step 5: Delete Old Session File

The old session file was created with the old API credentials, so delete it:

```bash
# Delete old session
rm trading_bot_session.session
rm trading_bot_session.session-journal  # if it exists

# Or on Windows:
del trading_bot_session.session
del trading_bot_session.session-journal
```

### Step 6: Try Authentication Again

Now run the bot with your new credentials:

```bash
python3 trading_bot.py
```

Or use the auth script:

```bash
python3 auth_telegram.py
```

You should now be able to receive verification codes with the new API credentials!

## Why This Works

- Different API apps sometimes have different rate limits
- New credentials = fresh start with Telegram's verification system
- Some API apps may have better delivery rates

## Troubleshooting

### Still Not Receiving Codes?

1. **Wait 10-15 minutes** between attempts
2. **Check your phone number format**: Must include country code with `+` (e.g., `+37495123434`)
3. **Try different phone number**: If you have another number, try that
4. **Check Telegram app**: Sometimes codes appear in the Telegram app itself
5. **Use Telegram Desktop**: Try logging in via Telegram Desktop first, then use that session

### Can't Access my.telegram.org?

- Make sure you're using the same phone number
- Try a different browser
- Clear browser cache
- Use incognito/private mode

### Multiple API Apps

You can create multiple API apps - Telegram allows this. Each app has its own:
- api_id
- api_hash
- Rate limits

## Quick Reference

**Get API Credentials**: https://my.telegram.org/apps

**Update .env**:
```
TELEGRAM_APP_ID=new_id
TELEGRAM_API_HASH=new_hash
```

**Delete old session**:
```bash
rm trading_bot_session.session*
```

**Try again**:
```bash
python3 trading_bot.py
```
