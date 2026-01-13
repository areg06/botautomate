# PythonAnywhere Setup Guide

## ⚠️ Important: Connection Restrictions

**PythonAnywhere FREE accounts block outbound connections to Telegram!**

- Free accounts can only make HTTP/HTTPS requests to whitelisted domains
- Telegram's MTProto protocol uses port 443 which is blocked
- **You need a PAID PythonAnywhere account ($5/month) to use Telegram**

**Alternative free hosting options:**
- Railway.app (free tier: $5 credit/month)
- Render.com (free tier: 750 hours/month)
- Oracle Cloud Always Free (permanent free VPS)

If you're on a free account, consider switching to one of the alternatives above.

## Setting Up Environment Variables (.env file)

PythonAnywhere doesn't support `.env` files directly, but you can set environment variables in the web interface.

### Method 1: Using PythonAnywhere Web Interface (Recommended)

1. **Log in to PythonAnywhere**:
   - Go to [pythonanywhere.com](https://www.pythonanywhere.com)
   - Log in to your account

2. **Navigate to Web App** (if using web app):
   - Click on "Web" tab
   - Click on your web app
   - Scroll down to "Environment variables" section

3. **Or use Files tab** (for console/always-on tasks):
   - Go to "Files" tab
   - Navigate to your project directory
   - You can create a `.env` file here, but it's better to use environment variables

4. **Set Environment Variables**:
   - In the "Environment variables" section (Web tab)
   - Or in "Tasks" → "Always-on task" settings
   - Add each variable one by one:
     ```
     BINANCE_API_KEY=your_binance_api_key_here
     BINANCE_API_SECRET=your_binance_api_secret_here
     TELEGRAM_APP_ID=your_telegram_app_id_here
     TELEGRAM_API_HASH=your_telegram_api_hash_here
     TELEGRAM_CHANNEL_ID=your_channel_id_here
     DRY_RUN=true
     PORT=8000
     ```

### Method 2: Create .env File via Files Tab

1. **Go to Files tab**:
   - Click "Files" in the top menu
   - Navigate to your project directory (e.g., `/home/yourusername/autmomate`)

2. **Create .env file**:
   - Click "New file"
   - Name it `.env` (with the dot at the beginning)
   - Paste your environment variables:
     ```
     BINANCE_API_KEY=your_binance_api_key_here
     BINANCE_API_SECRET=your_binance_api_secret_here
     TELEGRAM_APP_ID=your_telegram_app_id_here
     TELEGRAM_API_HASH=your_telegram_api_hash_here
     TELEGRAM_CHANNEL_ID=your_channel_id_here
     DRY_RUN=true
     PORT=8000
     ```
   - Click "Save"

3. **Verify the file**:
   - The file should appear in your file list
   - Make sure it's named exactly `.env` (not `env` or `.env.txt`)

### Method 3: Upload .env File from Local

1. **Prepare your .env file locally**:
   - Make sure your `.env` file is ready with all variables

2. **Upload via Files tab**:
   - Go to "Files" tab in PythonAnywhere
   - Navigate to your project directory
   - Click "Upload a file"
   - Select your `.env` file
   - Make sure it uploads as `.env` (not `.env.txt`)

3. **Verify upload**:
   - Check that the file appears in your directory
   - Click on it to verify contents

## Setting Up the Bot on PythonAnywhere

### Step 1: Upload Your Code

1. **Via Git** (Recommended):
   ```bash
   # In PythonAnywhere Bash console
   cd ~
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git automomate
   cd automomate
   ```

2. **Or upload files manually**:
   - Use "Files" tab → "Upload a file"
   - Upload all your Python files

### Step 2: Install Dependencies

1. **Open Bash console**:
   - Click "Consoles" → "Bash"

2. **Navigate to project**:
   ```bash
   cd ~/autmomate
   ```

3. **Install dependencies**:
   ```bash
   pip3.10 install --user -r requirements.txt
   ```

### Step 3: Set Environment Variables

Use one of the methods above to set your environment variables.

### Step 4: Test the Bot

1. **Run in console first** (to authenticate Telegram):
   ```bash
   cd ~/autmomate
   python3.10 trading_bot.py
   ```

2. **Authenticate Telegram**:
   - Enter your phone number
   - Enter verification code
   - Session will be saved

3. **Stop the bot** (Ctrl+C)

### Step 5: Set Up Always-On Task

1. **Go to "Tasks" tab**:
   - Click "Tasks" in top menu
   - Click "Create a new always-on task"

2. **Configure the task**:
   - **Command**: `cd ~/autmomate && python3.10 trading_bot.py`
   - **Working directory**: `/home/yourusername/autmomate`
   - **Environment variables**: Set them here or use .env file

3. **Start the task**:
   - Click "Run" or enable the task
   - Check logs to verify it's running

## Important Notes

### Environment Variables Priority

PythonAnywhere uses environment variables in this order:
1. Environment variables set in Web app settings (highest priority)
2. Environment variables in Always-on task settings
3. `.env` file in project directory (if python-dotenv loads it)

### For Always-On Tasks

If using an Always-on task, you can:
- Set environment variables in the task settings
- Or use a `.env` file in the working directory
- The bot will automatically load from `.env` using `python-dotenv`

### File Permissions

Make sure your `.env` file has correct permissions:
```bash
chmod 600 ~/autmomate/.env  # Only you can read/write
```

### Verify Environment Variables

Test if variables are loaded:
```bash
cd ~/autmomate
python3.10 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('BINANCE_API_KEY:', 'SET' if os.getenv('BINANCE_API_KEY') else 'NOT SET')"
```

## Troubleshooting

### .env file not loading
- Check file name is exactly `.env` (not `.env.txt`)
- Verify file is in the same directory as `trading_bot.py`
- Check file permissions: `ls -la ~/autmomate/.env`

### Environment variables not found
- Use the web interface to set them directly
- Or verify `.env` file contents
- Check working directory matches where `.env` is located

### Bot can't find .env
- Make sure you're running from the project directory
- Use absolute path: `load_dotenv('/home/yourusername/autmomate/.env')`

## Quick Setup Checklist

- [ ] Upload code to PythonAnywhere
- [ ] Install dependencies (`pip3.10 install --user -r requirements.txt`)
- [ ] Create `.env` file or set environment variables
- [ ] Test bot in console to authenticate Telegram
- [ ] Set up Always-on task
- [ ] Verify bot is running and monitoring channel
