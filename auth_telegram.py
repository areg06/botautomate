#!/usr/bin/env python3
"""
One-time Telegram authentication script.
Run this locally or via Railway CLI to authenticate Telegram.
"""

import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

load_dotenv()

async def authenticate():
    """Authenticate Telegram and save session."""
    api_id = int(os.getenv('TELEGRAM_APP_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        print("ERROR: TELEGRAM_APP_ID and TELEGRAM_API_HASH must be set in .env")
        return
    
    # Use the same session path as the main bot
    session_path = os.path.join(os.path.dirname(__file__), 'trading_bot_session')
    client = TelegramClient(session_path, api_id, api_hash)
    
    try:
        await client.start()
        
        if await client.is_user_authorized():
            print("✅ Already authenticated! Session file saved.")
            print(f"Session file location: {session_path}.session")
        else:
            print("❌ Authentication failed. Please try again.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    print("=" * 60)
    print("Telegram Authentication Script")
    print("=" * 60)
    print("This will authenticate your Telegram account and save the session.")
    print("You only need to run this once.")
    print("=" * 60)
    print()
    
    asyncio.run(authenticate())
