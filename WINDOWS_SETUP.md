# Windows Setup Guide

## Prerequisites

1. **Install Python 3.11 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify installation: Open Command Prompt and run:
     ```cmd
     python --version
     ```

2. **Install Git** (optional, if cloning from GitHub)
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Use default settings during installation

## Step-by-Step Setup

### Step 1: Open Command Prompt or PowerShell

- Press `Win + R`, type `cmd` and press Enter
- Or search for "Command Prompt" or "PowerShell" in Start menu

### Step 2: Navigate to Project Directory

```cmd
cd C:\path\to\autmomate
```

Or if you cloned from GitHub:
```cmd
cd C:\Users\YourUsername\Desktop\autmomate
```

### Step 3: Create Virtual Environment (Recommended)

```cmd
python -m venv venv
```

Activate virtual environment:
```cmd
venv\Scripts\activate
```

You should see `(venv)` in your prompt.

### Step 4: Install Dependencies

```cmd
pip install -r requirements.txt
```

If you get permission errors, use:
```cmd
pip install --user -r requirements.txt
```

### Step 5: Create .env File

**Option A: Using Notepad**
```cmd
notepad .env
```

**Option B: Using PowerShell**
```powershell
New-Item -Path .env -ItemType File
notepad .env
```

**Option C: Using Command Prompt (copy from example)**
```cmd
copy .env.example .env
notepad .env
```

Then edit `.env` file with your credentials:
```
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
TELEGRAM_APP_ID=your_telegram_app_id_here
TELEGRAM_API_HASH=your_telegram_api_hash_here
TELEGRAM_CHANNEL_ID=your_channel_id_here
DRY_RUN=true
PORT=8000
```

Save and close the file.

### Step 6: First-Time Telegram Authentication

Run the bot:
```cmd
python trading_bot.py
```

When prompted:
1. Enter your phone number (with country code, e.g., `+1234567890`)
2. Enter the verification code sent to your Telegram
3. If you have 2FA, enter your password

The session file will be saved automatically.

### Step 7: Run the Bot

After authentication, the bot will start monitoring. To run it again later:

```cmd
python trading_bot.py
```

## Running in Background (Windows)

### Option 1: Run in Separate Window

1. Create a batch file `run_bot.bat`:
```cmd
@echo off
cd /d "C:\path\to\autmomate"
venv\Scripts\activate
python trading_bot.py
pause
```

2. Double-click `run_bot.bat` to run

### Option 2: Run as Windows Service (Advanced)

Use NSSM (Non-Sucking Service Manager):
1. Download NSSM from [nssm.cc](https://nssm.cc/download)
2. Extract and run:
```cmd
nssm install TradingBot
```
3. Configure:
   - Path: `C:\Python\python.exe` (or your Python path)
   - Startup directory: `C:\path\to\autmomate`
   - Arguments: `trading_bot.py`

### Option 3: Use Task Scheduler

1. Open Task Scheduler (search in Start menu)
2. Create Basic Task
3. Set trigger (e.g., "At startup" or "At log on")
4. Action: Start a program
   - Program: `python.exe`
   - Arguments: `trading_bot.py`
   - Start in: `C:\path\to\autmomate`

## Common Windows Commands

### Check if Python is installed
```cmd
python --version
```

### Check if pip is installed
```cmd
pip --version
```

### Install a package
```cmd
pip install package_name
```

### List installed packages
```cmd
pip list
```

### View logs in real-time
If running in Command Prompt, logs will appear in the window.

### Stop the bot
Press `Ctrl + C` in the Command Prompt window

## Troubleshooting

### "python is not recognized"
- Python is not in PATH
- Reinstall Python and check "Add Python to PATH"
- Or use full path: `C:\Python\python.exe trading_bot.py`

### "pip is not recognized"
- Install pip: `python -m ensurepip --upgrade`
- Or use: `python -m pip install -r requirements.txt`

### Permission errors
- Run Command Prompt as Administrator
- Or use: `pip install --user -r requirements.txt`

### Module not found errors
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Port already in use
- Change PORT in .env file
- Or close the program using port 8000

### File path issues
- Use forward slashes or double backslashes: `C:\\path\\to\\file`
- Or use raw strings: `r"C:\path\to\file"`

## Quick Start Commands (Copy-Paste)

```cmd
REM Navigate to project
cd C:\path\to\autmomate

REM Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Create .env file (if not exists)
copy .env.example .env

REM Edit .env file
notepad .env

REM Run the bot
python trading_bot.py
```

## Running Multiple Instances

If you want to run multiple bots or test different configurations:

1. Create separate directories for each instance
2. Copy the project files
3. Create separate .env files
4. Run each in a separate Command Prompt window

## Accessing Web Interface

Once the bot is running, open your browser and go to:
```
http://localhost:8000
```

You'll see the status page and live logs.

## Stopping the Bot

- Press `Ctrl + C` in the Command Prompt
- Or close the Command Prompt window
- If running as service, use: `nssm stop TradingBot`
