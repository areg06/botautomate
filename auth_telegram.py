#!/usr/bin/env python3
"""
One-time Telegram authentication script.
Run this locally or via Railway CLI to authenticate Telegram.
"""

import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, FloodWaitError

load_dotenv()

async def authenticate():
    """Authenticate Telegram and save session."""
    api_id = os.getenv('TELEGRAM_APP_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        print("ERROR: TELEGRAM_APP_ID and TELEGRAM_API_HASH must be set in .env")
        return
    
    try:
        api_id = int(api_id)
    except ValueError:
        print("ERROR: TELEGRAM_APP_ID must be a valid integer")
        return
    
    # Use the same session path as the main bot
    session_path = os.path.join(os.path.dirname(__file__), 'trading_bot_session')
    client = TelegramClient(session_path, api_id, api_hash)
    
    try:
        print("\nConnecting to Telegram...")
        await client.connect()
        
        if not await client.is_user_authorized():
            print("\n" + "=" * 60)
            print("TELEGRAM AUTHENTICATION REQUIRED")
            print("=" * 60)
            
            # Get phone number
            phone = input("\nEnter your phone number (with country code, e.g., +1234567890): ").strip()
            
            if not phone.startswith('+'):
                print("⚠️  Warning: Phone number should start with + (country code)")
                phone = '+' + phone.lstrip('+')
            
            try:
                # Send code
                print(f"\n📱 Sending verification code to {phone}...")
                print("   This may take a few seconds...")
                
                sent_code = await client.send_code_request(phone)
                print(f"✅ Code sent! Login hash: {sent_code.phone_code_hash[:10]}...")
                
                # Try to get code
                print("\n" + "-" * 60)
                print("OPTIONS:")
                print("1. Enter the code sent via SMS to your Telegram app")
                print("2. Type 'call' to receive code via phone call instead")
                print("3. Type 'resend' to request a new code")
                print("-" * 60)
                
                max_attempts = 5
                for attempt in range(max_attempts):
                    code_input = input(f"\nEnter verification code (attempt {attempt + 1}/{max_attempts}): ").strip()
                    
                    if code_input.lower() == 'call':
                        print("\n📞 Requesting code via phone call...")
                        try:
                            sent_code = await client.send_code_request(phone, force_sms=False)
                            print("✅ Phone call initiated! Answer the call to get your code.")
                            code_input = input("\nEnter the code from the phone call: ").strip()
                        except FloodWaitError as e:
                            print(f"❌ Rate limited. Please wait {e.seconds} seconds before trying again.")
                            continue
                        except Exception as e:
                            print(f"❌ Error requesting phone call: {e}")
                            print("   Try entering the SMS code instead.")
                            continue
                    
                    if code_input.lower() == 'resend':
                        print("\n🔄 Resending code...")
                        try:
                            sent_code = await client.send_code_request(phone)
                            print("✅ New code sent!")
                            continue
                        except FloodWaitError as e:
                            print(f"❌ Rate limited. Please wait {e.seconds} seconds.")
                            continue
                        except Exception as e:
                            print(f"❌ Error resending code: {e}")
                            continue
                    
                    if not code_input.isdigit():
                        print("❌ Code must be numeric. Try again.")
                        continue
                    
                    try:
                        # Try to sign in with code
                        await client.sign_in(phone, code_input, phone_code_hash=sent_code.phone_code_hash)
                        print("\n✅ Code accepted!")
                        break
                    except PhoneCodeInvalidError:
                        print(f"❌ Invalid code. Please try again.")
                        if attempt < max_attempts - 1:
                            print("   You can also type 'resend' to get a new code or 'call' for phone call.")
                        continue
                    except SessionPasswordNeededError:
                        print("\n🔐 Two-factor authentication is enabled.")
                        password = input("Enter your 2FA password: ").strip()
                        try:
                            await client.sign_in(password=password)
                            print("✅ 2FA password accepted!")
                            break
                        except Exception as e:
                            print(f"❌ 2FA password error: {e}")
                            return
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        if attempt < max_attempts - 1:
                            continue
                        else:
                            return
                else:
                    print("\n❌ Maximum attempts reached. Please try again later.")
                    return
                
            except FloodWaitError as e:
                print(f"\n❌ Rate limited by Telegram. Please wait {e.seconds} seconds ({e.seconds // 60} minutes) before trying again.")
                return
            except Exception as e:
                print(f"\n❌ Error during authentication: {e}")
                print("\nTroubleshooting tips:")
                print("1. Make sure your phone number is correct (include country code with +)")
                print("2. Check if you have an active internet connection")
                print("3. Try again in a few minutes if you've made multiple attempts")
                print("4. Make sure your Telegram app is working on your phone")
                return
        
        # Verify authorization
        if await client.is_user_authorized():
            me = await client.get_me()
            print("\n" + "=" * 60)
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print("=" * 60)
            print(f"Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or 'no username'})")
            print(f"Phone: {me.phone}")
            print(f"\nSession file saved: {session_path}.session")
            print("You can now run the trading bot!")
            print("=" * 60)
        else:
            print("\n❌ Authentication failed. Please try again.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Authentication cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

if __name__ == '__main__':
    print("=" * 60)
    print("Telegram Authentication Script")
    print("=" * 60)
    print("This will authenticate your Telegram account and save the session.")
    print("You only need to run this once.")
    print("=" * 60)
    
    asyncio.run(authenticate())
