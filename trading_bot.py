#!/usr/bin/env python3
"""
Telegram Signal Trading Bot for Binance Futures
Monitors Telegram channel for trading signals and executes trades automatically.
"""

import os
import re
import asyncio
import logging
import threading
from typing import Optional, Dict, List
from decimal import Decimal, ROUND_DOWN
from dataclasses import dataclass
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
import ccxt
from ccxt.base.errors import InsufficientFunds, NetworkError, ExchangeError

# Load environment variables
# Try to load from .env file in current directory, or use system environment variables
load_dotenv()
# Also try loading from absolute path (useful for PythonAnywhere)
if not os.getenv('BINANCE_API_KEY'):
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)

# Import shared log storage
from log_storage import log_storage

# Custom log handler to store logs in memory for web display
class WebLogHandler(logging.Handler):
    """Log handler that stores logs in memory for web display."""
    def emit(self, record):
        """Store log record in memory."""
        try:
            log_entry = self.format(record)
            log_storage.add_log(log_entry)
        except Exception:
            pass

# Create web log handler
web_log_handler = WebLogHandler()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        web_log_handler  # Web display
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TradingSignal:
    """Represents a parsed trading signal."""
    direction: str  # "BUY" or "SELL"
    symbol: str  # e.g., "ETH/USDT"
    leverage: float
    entry_price: float
    targets: List[float]


class SignalParser:
    """Parses trading signals from Telegram messages using regex."""
    
    @staticmethod
    def parse_signal(message_text: str) -> Optional[TradingSignal]:
        """
        Parse a trading signal from message text.
        
        Returns TradingSignal if valid, None otherwise.
        """
        try:
            # Extract direction
            direction_match = re.search(r'(🟢 Long|🔴 Short)', message_text)
            if not direction_match:
                logger.warning("No direction found in signal")
                return None
            
            direction_str = direction_match.group(1)
            direction = "BUY" if "🟢 Long" in direction_str else "SELL"
            
            # Extract symbol
            symbol_match = re.search(r'Name:\s*([A-Z]+/USDT)', message_text)
            if not symbol_match:
                logger.warning("No symbol found in signal")
                return None
            
            symbol = symbol_match.group(1)
            
            # Extract leverage
            leverage_match = re.search(r'Margin mode:\s*Cross\s*\(([\d.]+)X\)', message_text)
            if not leverage_match:
                logger.warning("No leverage found in signal")
                return None
            
            leverage = float(leverage_match.group(1))
            
            # Extract entry price
            entry_match = re.search(r'Entry price\(USDT\):\s*([\d.]+)', message_text, re.MULTILINE)
            if not entry_match:
                logger.warning("No entry price found in signal")
                return None
            
            entry_price = float(entry_match.group(1))
            
            # Extract targets
            targets = []
            target_pattern = r'(\d+)\)\s*([\d.]+)'
            target_matches = re.findall(target_pattern, message_text)
            
            for _, target_price in target_matches:
                targets.append(float(target_price))
            
            if not targets:
                logger.warning("No targets found in signal")
                return None
            
            # Sort targets to ensure correct order
            if direction == "BUY":
                targets.sort()  # Ascending for long
            else:
                targets.sort(reverse=True)  # Descending for short
            
            signal = TradingSignal(
                direction=direction,
                symbol=symbol,
                leverage=leverage,
                entry_price=entry_price,
                targets=targets[:1]  # Only take first target (100% of position)
            )
            
            logger.info(f"Parsed signal: {signal.direction} {signal.symbol} @ {signal.entry_price} "
                       f"with {signal.leverage}X leverage, {len(signal.targets)} targets")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error parsing signal: {e}")
            return None


class BinanceFuturesTrader:
    """Handles trading operations on Binance Futures using CCXT."""
    
    def __init__(self, api_key: str, api_secret: str, dry_run: bool = False, notification_callback=None):
        """
        Initialize Binance Futures trader.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            dry_run: If True, only print actions without executing
            notification_callback: Async function to send notifications (signal, message)
        """
        self.dry_run = dry_run
        self.notification_callback = notification_callback
        self.active_trades = {}  # Track active trades: {symbol: {entry_price, position_size, targets, tp_orders}}
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # Use futures
            },
            'sandbox': False,  # Always use live API, dry_run just prevents execution
        })
        
        if dry_run:
            logger.warning("=" * 60)
            logger.warning("⚠️  DRY RUN MODE: No actual trades will be executed")
            logger.warning("=" * 60)
            logger.warning("To execute real trades, set DRY_RUN=false in environment variables")
        else:
            logger.warning("=" * 60)
            logger.warning("🚨 LIVE MODE: Trades WILL be executed on Binance Futures")
            logger.warning("=" * 60)
    
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """
        Set leverage for a symbol.
        
        Args:
            symbol: Trading pair (e.g., "ETH/USDT")
            leverage: Leverage value (e.g., 100)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would set leverage to {leverage}X for {symbol}")
                return True
            
            # Binance futures uses set_leverage method
            logger.info(f"Setting leverage to {leverage}X for {symbol}...")
            self.exchange.set_leverage(leverage, symbol)
            logger.info(f"✅ Successfully set leverage to {leverage}X for {symbol}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error setting leverage: {e}")
            
            # Check for specific Binance API errors
            if "-2015" in error_msg or "Invalid API-key" in error_msg or "permissions" in error_msg:
                logger.error("=" * 60)
                logger.error("❌ BINANCE API PERMISSION ERROR")
                logger.error("=" * 60)
                logger.error("Your Binance API key doesn't have the required permissions.")
                logger.error("")
                logger.error("To fix this:")
                logger.error("1. Go to Binance → API Management")
                logger.error("2. Edit your API key")
                logger.error("3. Enable 'Enable Futures' permission")
                logger.error("4. If using IP whitelist, add Render's IP or disable whitelist")
                logger.error("5. Save and wait 5 minutes for changes to take effect")
                logger.error("=" * 60)
            elif "IP" in error_msg or "whitelist" in error_msg.lower():
                logger.error("=" * 60)
                logger.error("❌ BINANCE IP WHITELIST ERROR")
                logger.error("=" * 60)
                logger.error("Your IP is not whitelisted in Binance API settings.")
                logger.error("")
                logger.error("To fix this:")
                logger.error("1. Go to Binance → API Management")
                logger.error("2. Edit your API key")
                logger.error("3. Either:")
                logger.error("   - Disable IP whitelist (less secure)")
                logger.error("   - Add Render's server IPs to whitelist")
                logger.error("4. Save changes")
                logger.error("=" * 60)
            
            return False
    
    def get_balance(self) -> Optional[float]:
        """Get USDT balance from futures account."""
        try:
            if self.dry_run:
                logger.info("[DRY RUN] Would fetch balance")
                return 1000.0  # Mock balance for dry run
            
            balance = self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0.0)
            logger.info(f"Current USDT balance: {usdt_balance}")
            return usdt_balance
            
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return None
    
    def calculate_position_size(self, balance: float, entry_price: float, leverage: float) -> float:
        """
        Calculate position size based on balance and leverage.
        Uses 15% of account balance.
        
        Args:
            balance: Available USDT balance
            entry_price: Entry price
            leverage: Leverage multiplier
        
        Returns:
            Position size in base currency
        """
        # Use 15% of balance for position
        usable_balance = balance * 0.15
        # Position size = (balance * leverage) / entry_price
        position_size = (usable_balance * leverage) / entry_price
        return float(Decimal(str(position_size)).quantize(Decimal('0.001'), rounding=ROUND_DOWN))
    
    def place_market_order(self, signal: TradingSignal, position_size: float) -> Optional[str]:
        """
        Place a market order for entry.
        
        Args:
            signal: Trading signal
            position_size: Position size in base currency
        
        Returns:
            Order ID if successful, None otherwise
        """
        try:
            side = 'buy' if signal.direction == "BUY" else 'sell'
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would place {side} market order: "
                          f"{position_size} {signal.symbol} @ market price")
                return "dry_run_order_id"
            
            logger.info(f"Placing {side} market order: {position_size} {signal.symbol}...")
            order = self.exchange.create_market_order(
                symbol=signal.symbol,
                side=side,
                amount=position_size
            )
            
            order_id = order.get('id')
            logger.info(f"✅ Successfully placed {side} market order: {order_id} "
                       f"for {position_size} {signal.symbol} @ {order.get('price', 'market price')}")
            return order_id
            
        except InsufficientFunds as e:
            logger.error(f"Insufficient funds: {e}")
            return None
        except NetworkError as e:
            logger.error(f"Network error: {e}")
            return None
        except ExchangeError as e:
            logger.error(f"Exchange error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            return None
    
    def place_stop_loss_order(self, signal: TradingSignal, entry_price: float, 
                              position_size: float, leverage: float) -> Optional[str]:
        """
        Place a stop loss order at -170% ROI.
        
        Args:
            signal: Trading signal
            entry_price: Entry price
            position_size: Full position size
            leverage: Leverage multiplier
        
        Returns:
            Order ID if successful, None otherwise
        """
        try:
            # Calculate stop loss price for -170% ROI
            # ROI = (SL - entry) / entry * leverage = -1.70
            # (SL - entry) / entry = -1.70 / leverage
            # SL = entry * (1 - 1.70 / leverage)
            
            if signal.direction == "BUY":
                # For LONG: SL below entry
                sl_price = entry_price * (1 - 1.70 / leverage)
            else:
                # For SHORT: SL above entry
                sl_price = entry_price * (1 + 1.70 / leverage)
            
            # For stop loss, we need to close the position
            # If we bought (long), we sell to stop loss
            # If we sold (short), we buy to stop loss
            side = 'sell' if signal.direction == "BUY" else 'buy'
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would place stop loss: "
                          f"{side} {position_size} {signal.symbol} @ {sl_price:.6f} (-170% ROI)")
                return "dry_run_sl"
            
            logger.info(f"Placing stop loss: {side} {position_size} {signal.symbol} @ {sl_price:.6f}...")
            # Binance Futures requires using Algo Order API for stop loss
            # Use STOP_MARKET via create_order with proper params
            try:
                # Method 1: Try STOP_MARKET with reduceOnly
                order = self.exchange.create_order(
                    symbol=signal.symbol,
                    type='STOP_MARKET',
                    side=side,
                    amount=position_size,
                    params={
                        'stopPrice': sl_price,
                        'reduceOnly': True,
                        'workingType': 'MARK_PRICE'  # Use mark price for stop loss
                    }
                )
            except Exception as e:
                # Fallback: Try using STOP with limit price
                logger.warning(f"Stop market order failed, trying STOP limit: {e}")
                try:
                    # Calculate a limit price slightly worse than stop price
                    if side == 'sell':
                        limit_price = sl_price * 0.995  # 0.5% below stop for sell
                    else:
                        limit_price = sl_price * 1.005  # 0.5% above stop for buy
                    
                    order = self.exchange.create_order(
                        symbol=signal.symbol,
                        type='STOP',
                        side=side,
                        amount=position_size,
                        price=limit_price,
                        params={
                            'stopPrice': sl_price,
                            'reduceOnly': True,
                            'workingType': 'MARK_PRICE'
                        }
                    )
                except Exception as e2:
                    # Last resort: Use TAKE_PROFIT_MARKET in reverse (not ideal but works)
                    logger.warning(f"STOP order failed, trying alternative method: {e2}")
                    try:
                        # Use limit order as stop loss (less ideal but functional)
                        order = self.exchange.create_limit_order(
                            symbol=signal.symbol,
                            side=side,
                            amount=position_size,
                            price=sl_price
                        )
                        logger.warning("Using limit order as stop loss (less reliable than stop market)")
                    except Exception as e3:
                        logger.error(f"All stop loss methods failed: {e3}")
                        logger.warning("Continuing without stop loss - monitor position manually!")
                        return None
            
            order_id = order.get('id')
            logger.info(f"✅ Successfully placed stop loss: {order_id} "
                       f"for {position_size} {signal.symbol} @ {sl_price:.6f} (-170% ROI)")
            return order_id
            
        except Exception as e:
            logger.error(f"Error placing stop loss order: {e}")
            return None
    
    def place_take_profit_order(self, signal: TradingSignal, target_price: float, 
                                position_size: float, order_num: int) -> Optional[str]:
        """
        Place a take profit limit order.
        
        Args:
            signal: Trading signal
            target_price: Target price for take profit
            position_size: Position size to close (60% for first, 40% for second)
            order_num: Order number (1 or 2)
        
        Returns:
            Order ID if successful, None otherwise
        """
        try:
            # For take profit, we need to close the position
            # If we bought (long), we sell to take profit
            # If we sold (short), we buy to take profit
            side = 'sell' if signal.direction == "BUY" else 'buy'
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would place take profit {order_num}: "
                          f"{side} {position_size} {signal.symbol} @ {target_price}")
                return f"dry_run_tp_{order_num}"
            
            logger.info(f"Placing take profit {order_num}: {side} {position_size} {signal.symbol} @ {target_price}...")
            order = self.exchange.create_limit_order(
                symbol=signal.symbol,
                side=side,
                amount=position_size,
                price=target_price
            )
            
            order_id = order.get('id')
            logger.info(f"✅ Successfully placed take profit {order_num}: {order_id} "
                       f"for {position_size} {signal.symbol} @ {target_price}")
            return order_id
            
        except Exception as e:
            logger.error(f"Error placing take profit order {order_num}: {e}")
            return None
    
    def execute_signal(self, signal: TradingSignal) -> bool:
        """
        Execute a complete trading signal.
        
        Args:
            signal: Trading signal to execute
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Executing signal: {signal.direction} {signal.symbol}")
            
            # Step 1: Set leverage
            if not self.set_leverage(signal.symbol, int(signal.leverage)):
                logger.error("Failed to set leverage")
                return False
            
            # Step 2: Get balance
            balance = self.get_balance()
            if balance is None or balance <= 0:
                logger.error("Invalid or insufficient balance")
                return False
            
            # Step 3: Calculate position size
            position_size = self.calculate_position_size(
                balance, signal.entry_price, signal.leverage
            )
            
            if position_size <= 0:
                logger.error("Invalid position size calculated")
                return False
            
            logger.info(f"Calculated position size: {position_size} {signal.symbol.split('/')[0]}")
            
            # Step 4: Place market order for entry
            entry_order_id = self.place_market_order(signal, position_size)
            if not entry_order_id:
                logger.error("Failed to place entry order")
                return False
            
            # Step 5: Place stop loss order (-170% ROI)
            sl_order_id = self.place_stop_loss_order(
                signal, signal.entry_price, position_size, signal.leverage
            )
            if not sl_order_id:
                logger.warning("Failed to place stop loss order")
            
            # Step 6: Place take profit order
            # Close 100% of position at first TP price
            if len(signal.targets) < 1:
                logger.warning(f"Signal has no targets")
                return False
            
            # Use 100% of position for first TP
            tp_size = position_size  # 100% of position
            tp_size = float(Decimal(str(tp_size)).quantize(Decimal('0.001'), rounding=ROUND_DOWN))
            
            tp_orders = []
            
            # Place take profit: Close 100% of position at first target price from signal
            logger.info(f"TP: Closing {tp_size} (100% of {position_size}) at price {signal.targets[0]}")
            tp_order_id = self.place_take_profit_order(
                signal, signal.targets[0], tp_size, 1
            )
            if tp_order_id:
                tp_orders.append(tp_order_id)
            else:
                logger.warning("Failed to place take profit order")
            
            logger.info(f"Successfully executed signal: Entry order {entry_order_id}, "
                       f"Stop loss {sl_order_id}, {len(tp_orders)} take profit orders placed")
            
            # Store trade info for tracking
            self.active_trades[signal.symbol] = {
                'entry_price': signal.entry_price,
                'position_size': position_size,
                'direction': signal.direction,
                'leverage': signal.leverage,
                'targets': signal.targets,
                'tp_orders': {
                    1: {'order_id': tp_order_id, 'price': signal.targets[0], 'size': tp_size}
                },
                'entry_order_id': entry_order_id
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return False


class TelegramSignalListener:
    """Listens to Telegram channel for trading signals."""
    
    def __init__(self, api_id: int, api_hash: str, channel_id: int, 
                 trader: BinanceFuturesTrader, notification_chat_id: Optional[int] = None):
        """
        Initialize Telegram listener.
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API hash
            channel_id: Channel ID to monitor
            trader: BinanceFuturesTrader instance
            notification_chat_id: Chat ID to send notifications to (optional)
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.channel_id = channel_id
        self.notification_chat_id = notification_chat_id
        self.trader = trader
        self.parser = SignalParser()
        self.client = None
    
    def _delete_corrupted_session(self, session_path: str):
        """Delete corrupted session files."""
        session_file = f"{session_path}.session"
        journal_file = f"{session_path}.session-journal"
        
        deleted = False
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                logger.warning(f"Deleted corrupted session file: {session_file}")
                deleted = True
            except Exception as e:
                logger.error(f"Failed to delete session file: {e}")
        
        if os.path.exists(journal_file):
            try:
                os.remove(journal_file)
                logger.warning(f"Deleted session journal file: {journal_file}")
            except Exception as e:
                logger.error(f"Failed to delete journal file: {e}")
        
        return deleted
    
    async def initialize(self):
        """Initialize Telegram client."""
        # Use absolute path for session file to ensure persistence in cloud environments
        session_path = os.path.join(os.path.dirname(__file__), 'trading_bot_session')
        self.client = TelegramClient(session_path, self.api_id, self.api_hash)
        
        try:
            # Check if we're in an interactive environment
            import sys
            is_interactive = sys.stdin.isatty()
            
            if not is_interactive:
                logger.warning("Non-interactive environment detected. Checking for existing session...")
            
            await self.client.connect()
            
            # Check if already authorized
            if not await self.client.is_user_authorized():
                if not is_interactive:
                    logger.error("=" * 60)
                    logger.error("TELEGRAM AUTHENTICATION REQUIRED")
                    logger.error("=" * 60)
                    logger.error("Please use Railway CLI to authenticate:")
                    logger.error("1. Run: railway shell")
                    logger.error("2. Run: python3 trading_bot.py")
                    logger.error("3. Enter your phone number and verification code")
                    logger.error("4. Session will be saved automatically")
                    logger.error("=" * 60)
                    raise SessionPasswordNeededError("Authentication required in interactive mode")
                
                # Interactive authentication with phone call and QR code support
                from telethon.errors import PhoneCodeInvalidError, FloodWaitError
                
                logger.info("=" * 60)
                logger.info("TELEGRAM AUTHENTICATION")
                logger.info("=" * 60)
                logger.info("Choose authentication method:")
                logger.info("1. Phone number + SMS/Call code (traditional)")
                logger.info("2. QR code (scan with your Telegram app)")
                logger.info("")
                
                auth_method = input("Enter method (1 or 2, default: 1): ").strip() or "1"
                
                if auth_method == "2":
                    # QR Code login
                    logger.info("")
                    logger.info("=" * 60)
                    logger.info("QR CODE LOGIN")
                    logger.info("=" * 60)
                    logger.info("Generating QR code...")
                    
                    try:
                        qr_login = await self.client.qr_login()
                        logger.info("")
                        logger.info("✅ QR code generated!")
                        logger.info("")
                        logger.info("📱 INSTRUCTIONS:")
                        logger.info("1. Open Telegram app on your phone")
                        logger.info("2. Go to Settings → Devices → Link Desktop Device")
                        logger.info("3. Scan the QR code below")
                        logger.info("")
                        logger.info("QR Code URL:")
                        logger.info(qr_login.url)
                        logger.info("")
                        
                        # Try to display QR code if qrcode library is available
                        try:
                            import qrcode
                            qr = qrcode.QRCode()
                            qr.add_data(qr_login.url)
                            qr.make(fit=True)
                            
                            # Try to show QR code image
                            try:
                                img = qr.make_image()
                                img.show()  # Opens image viewer
                                logger.info("✅ QR code image opened!")
                            except:
                                # Fallback to ASCII
                                logger.info("QR Code (ASCII):")
                                qr.print_ascii(invert=True)
                                logger.info("")
                        except ImportError:
                            logger.info("💡 Tip: Install 'qrcode' for visual QR code:")
                            logger.info("   pip install qrcode[pil]")
                            logger.info("")
                        except Exception as e:
                            logger.debug(f"Could not display QR code: {e}")
                        
                        logger.info("⏳ Waiting for you to scan the QR code...")
                        logger.info("(This will timeout after 60 seconds)")
                        logger.info("")
                        
                        try:
                            user = await qr_login.wait(timeout=60)
                            logger.info(f"✅ QR code scanned and accepted!")
                            
                            # Check if 2FA is needed after QR scan
                            if not await self.client.is_user_authorized():
                                logger.info("🔐 Two-factor authentication is enabled.")
                                password = input("Enter your 2FA password: ").strip()
                                try:
                                    await self.client.sign_in(password=password)
                                    logger.info("✅ 2FA password accepted!")
                                except Exception as e:
                                    logger.error(f"2FA password error: {e}")
                                    raise
                            
                            logger.info(f"Logged in as: {user.first_name} {user.last_name or ''}")
                        except asyncio.TimeoutError:
                            logger.error("⏰ QR code login timed out. Please try again.")
                            raise Exception("QR login timeout")
                        except Exception as e:
                            error_msg = str(e)
                            if "password" in error_msg.lower() or "2FA" in error_msg or "two-step" in error_msg.lower():
                                logger.warning("⚠️  QR code login requires 2FA password.")
                                logger.info("Falling back to phone number authentication...")
                                logger.info("")
                                auth_method = "1"  # Fall back to phone auth
                            else:
                                logger.error(f"QR login error: {e}")
                                raise
                            
                    except Exception as e:
                        error_msg = str(e)
                        if "password" in error_msg.lower() or "2FA" in error_msg or "two-step" in error_msg.lower() or "two-steps" in error_msg.lower():
                            logger.warning("=" * 60)
                            logger.warning("⚠️  QR CODE LOGIN NOT AVAILABLE")
                            logger.warning("=" * 60)
                            logger.warning("Your account has 2FA enabled.")
                            logger.warning("QR code login requires password first.")
                            logger.warning("")
                            logger.info("Falling back to phone number authentication...")
                            logger.info("")
                            auth_method = "1"  # Fall back to phone auth
                        else:
                            logger.error(f"QR code login failed: {e}")
                            logger.info("Falling back to phone number authentication...")
                            logger.info("")
                            auth_method = "1"  # Fall back to phone auth
                
                if auth_method == "1":
                    # Phone number authentication
                    logger.info("=" * 60)
                    logger.info("PHONE NUMBER AUTHENTICATION")
                    logger.info("=" * 60)
                    
                    phone = input("Enter your phone number (with country code, e.g., +1234567890): ").strip()
                if not phone.startswith('+'):
                    logger.warning("Phone number should start with + (country code)")
                    phone = '+' + phone.lstrip('+')
                
                try:
                    logger.info(f"Sending verification code to {phone}...")
                    sent_code = await self.client.send_code_request(phone)
                    logger.info("Code sent! Check your Telegram app.")
                    logger.info("")
                    logger.info("OPTIONS:")
                    logger.info("1. Enter the code sent via SMS to your Telegram app")
                    logger.info("2. Type 'call' to receive code via phone call instead")
                    logger.info("3. Type 'resend' to request a new SMS code")
                    logger.info("")
                    
                    max_attempts = 5
                    for attempt in range(max_attempts):
                        code_input = input(f"Enter verification code (attempt {attempt + 1}/{max_attempts}): ").strip()
                        
                        if code_input.lower() == 'call':
                            logger.info("Requesting code via phone call...")
                            try:
                                sent_code = await self.client.send_code_request(phone, force_sms=False)
                                logger.info("Phone call initiated! Answer the call to get your code.")
                                code_input = input("Enter the code from the phone call: ").strip()
                            except FloodWaitError as e:
                                wait_minutes = e.seconds // 60
                                logger.error("=" * 60)
                                logger.error(f"⏰ RATE LIMITED")
                                logger.error("=" * 60)
                                logger.error(f"Telegram has rate limited your requests.")
                                logger.error(f"Please wait {e.seconds} seconds ({wait_minutes} minutes) before trying again.")
                                logger.error("")
                                logger.error("You can:")
                                logger.error("1. Wait and try again later")
                                logger.error("2. Check your Telegram app - code might be there")
                                logger.error("3. Check your phone's SMS messages")
                                logger.error("=" * 60)
                                raise
                            except Exception as e:
                                error_msg = str(e)
                                if "all available options" in error_msg.lower() or "ResendCodeRequest" in error_msg:
                                    logger.error("=" * 60)
                                    logger.error("⚠️  ALL VERIFICATION METHODS USED")
                                    logger.error("=" * 60)
                                    logger.error("You've already used all available verification methods:")
                                    logger.error("- SMS code")
                                    logger.error("- Phone call")
                                    logger.error("")
                                    logger.error("Options:")
                                    logger.error("1. Check your Telegram app - code might be displayed there")
                                    logger.error("2. Check your phone's SMS messages")
                                    logger.error("3. Wait 5-10 minutes and try 'resend' for a new code")
                                    logger.error("4. Enter the code you already received (if you have it)")
                                    logger.error("=" * 60)
                                    logger.info("Try entering the SMS code you received, or wait and use 'resend'.")
                                else:
                                    logger.error(f"Error requesting phone call: {e}")
                                    logger.info("Try entering the SMS code instead.")
                                continue
                        
                        if code_input.lower() == 'resend':
                            logger.info("Resending code...")
                            try:
                                sent_code = await self.client.send_code_request(phone)
                                logger.info("✅ New code sent! Check your Telegram app or SMS.")
                                continue
                            except FloodWaitError as e:
                                wait_minutes = e.seconds // 60
                                logger.error("=" * 60)
                                logger.error(f"⏰ RATE LIMITED")
                                logger.error("=" * 60)
                                logger.error(f"Cannot resend code yet. Please wait {e.seconds} seconds ({wait_minutes} minutes).")
                                logger.error("")
                                logger.error("In the meantime:")
                                logger.error("- Check your Telegram app for the code")
                                logger.error("- Check your phone's SMS messages")
                                logger.error("=" * 60)
                                continue
                            except Exception as e:
                                error_msg = str(e)
                                if "all available options" in error_msg.lower():
                                    logger.error("⚠️  All verification methods already used. Please wait 5-10 minutes.")
                                    logger.info("Or try entering a code you already received.")
                                else:
                                    logger.error(f"Error resending code: {e}")
                                continue
                        
                        if not code_input.isdigit():
                            logger.error("Code must be numeric. Try again.")
                            continue
                        
                        try:
                            await self.client.sign_in(phone, code_input, phone_code_hash=sent_code.phone_code_hash)
                            logger.info("Code accepted!")
                            break
                        except PhoneCodeInvalidError:
                            logger.error(f"Invalid code. Please try again.")
                            if attempt < max_attempts - 1:
                                logger.info("You can type 'resend' to get a new code or 'call' for phone call.")
                            continue
                        except SessionPasswordNeededError:
                            logger.info("Two-factor authentication is enabled.")
                            password = input("Enter your 2FA password: ").strip()
                            try:
                                await self.client.sign_in(password=password)
                                logger.info("2FA password accepted!")
                                break
                            except Exception as e:
                                logger.error(f"2FA password error: {e}")
                                raise
                        except Exception as e:
                            logger.error(f"Error: {e}")
                            if attempt < max_attempts - 1:
                                continue
                            else:
                                raise
                    else:
                        raise Exception("Maximum authentication attempts reached")
                        
                except FloodWaitError as e:
                    logger.error(f"Rate limited by Telegram. Please wait {e.seconds} seconds ({e.seconds // 60} minutes).")
                    raise
                except Exception as e:
                    logger.error(f"Authentication error: {e}")
                    raise
            
            logger.info("Telegram client initialized successfully")
        except SessionPasswordNeededError:
            raise
        except Exception as e:
            error_msg = str(e)
            # Check for session corruption errors
            if "Could not find a matching Constructor ID" in error_msg or "misusing the session" in error_msg:
                logger.error("=" * 60)
                logger.error("SESSION CORRUPTION DETECTED")
                logger.error("=" * 60)
                logger.error("The Telegram session file is corrupted and will be deleted.")
                logger.error("You need to re-authenticate.")
                
                # Delete corrupted session
                if self._delete_corrupted_session(session_path):
                    logger.info("Corrupted session deleted. Please re-authenticate.")
                    logger.error("=" * 60)
                    logger.error("RE-AUTHENTICATION REQUIRED")
                    logger.error("=" * 60)
                    logger.error("Please use Railway CLI to authenticate:")
                    logger.error("1. Run: railway shell")
                    logger.error("2. Run: python3 trading_bot.py")
                    logger.error("3. Enter your phone number and verification code")
                    logger.error("=" * 60)
                
                raise SessionPasswordNeededError("Session corrupted, re-authentication required")
            else:
                error_msg = str(e)
                # Check for connection errors (common on PythonAnywhere)
                connection_errors = [
                    "ConnectionRefusedError",
                    "Connection failed",
                    "Connect call failed",
                    "Connection to Telegram failed"
                ]
                
                if any(err in error_msg for err in connection_errors):
                    logger.error("")
                    logger.error("=" * 60)
                    logger.error("❌ TELEGRAM CONNECTION ERROR")
                    logger.error("=" * 60)
                    logger.error("Cannot connect to Telegram servers.")
                    logger.error("")
                    logger.error("This is likely due to network restrictions:")
                    logger.error("")
                    logger.error("🔴 PythonAnywhere FREE accounts block outbound connections!")
                    logger.error("   - Free accounts can only make HTTP/HTTPS to whitelisted domains")
                    logger.error("   - Telegram's MTProto protocol is blocked")
                    logger.error("   - You need a PAID account ($5/month) to use Telegram")
                    logger.error("")
                    logger.error("✅ Alternative FREE hosting options:")
                    logger.error("   1. Railway.app - $5 credit/month (recommended)")
                    logger.error("   2. Render.com - 750 hours/month free")
                    logger.error("   3. Oracle Cloud - Always Free VPS")
                    logger.error("")
                    logger.error("All of these allow outbound connections to Telegram.")
                    logger.error("=" * 60)
                    logger.error("")
                else:
                    logger.error(f"Failed to initialize Telegram client: {e}")
                    logger.info("If this is first run, you need to authenticate interactively.")
            raise
    
    async def send_notification(self, message: str):
        """Send notification message to notification chat."""
        if not self.notification_chat_id or not self.client:
            return
        
        try:
            # Get entity first to ensure it's resolved
            try:
                entity = await self.client.get_entity(self.notification_chat_id)
            except Exception:
                # If get_entity fails, try with InputPeerUser
                from telethon.tl.types import InputPeerUser
                entity = InputPeerUser(self.notification_chat_id, 0)  # access_hash=0, will be resolved
            
            await self.client.send_message(entity, message)
            logger.info(f"Notification sent to chat {self.notification_chat_id}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            logger.debug(f"Error details: {type(e).__name__}: {e}")
    
    async def forward_signal(self, event):
        """Forward signal message to notification chat."""
        if not self.notification_chat_id or not self.client:
            return
        
        try:
            # Get entity first to ensure it's resolved
            try:
                entity = await self.client.get_entity(self.notification_chat_id)
            except Exception:
                # If get_entity fails, try with InputPeerUser
                from telethon.tl.types import InputPeerUser
                entity = InputPeerUser(self.notification_chat_id, 0)  # access_hash=0, will be resolved
            
            await self.client.forward_messages(
                entity,
                event.message.id,
                self.channel_id
            )
            logger.info(f"Signal forwarded to chat {self.notification_chat_id}")
        except Exception as e:
            logger.error(f"Failed to forward signal: {e}")
            logger.debug(f"Error details: {type(e).__name__}: {e}")
    
    async def check_order_status(self, symbol: str):
        """Check if take profit orders were filled and send notifications."""
        if not self.trader or not hasattr(self.trader, 'active_trades'):
            return
        
        if symbol not in self.trader.active_trades:
            return
        
        trade = self.trader.active_trades[symbol]
        
        try:
            # Check each TP order
            for tp_num, tp_info in trade['tp_orders'].items():
                if not tp_info['order_id'] or tp_info['order_id'].startswith('dry_run'):
                    continue
                
                # Skip if already notified (store in trade info)
                if f'tp{tp_num}_notified' in trade:
                    continue
                
                try:
                    order = self.trader.exchange.fetch_order(tp_info['order_id'], symbol)
                    if order['status'] == 'closed' or order['status'] == 'filled':
                        # Calculate profit percentage
                        entry_price = trade['entry_price']
                        tp_price = tp_info['price']
                        
                        if trade['direction'] == "BUY":
                            profit_pct = ((tp_price - entry_price) / entry_price) * 100 * trade['leverage']
                        else:  # SELL
                            profit_pct = ((entry_price - tp_price) / entry_price) * 100 * trade['leverage']
                        
                        # Send achievement notification
                        symbol_name = symbol.replace('/USDT', '')
                        message = f"💸 {symbol_name}\n✅ Target #{tp_num} Done\nCurrent profit: {profit_pct:.1f}%"
                        await self.send_notification(message)
                        
                        # Mark as notified
                        trade[f'tp{tp_num}_notified'] = True
                        
                        logger.info(f"Target #{tp_num} achieved for {symbol}: {profit_pct:.1f}% profit")
                        
                except Exception as e:
                    logger.debug(f"Error checking order {tp_info['order_id']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking order status: {e}")
    
    async def periodic_order_check(self):
        """Periodically check order status for all active trades."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                if self.trader and self.trader.active_trades:
                    for symbol in list(self.trader.active_trades.keys()):
                        await self.check_order_status(symbol)
            except Exception as e:
                logger.error(f"Error in periodic order check: {e}")
    
    async def handle_message(self, event):
        """Handle incoming message from Telegram channel."""
        try:
            message_text = event.message.message
            
            # Check if message contains trading signal indicators
            if '🟢 Long' not in message_text and '🔴 Short' not in message_text:
                return
            
            logger.info(f"Received potential signal message from channel {self.channel_id}")
            logger.debug(f"Message content: {message_text[:200]}...")
            
            # Forward signal to notification chat
            if self.notification_chat_id:
                await self.forward_signal(event)
            
            # Parse signal
            signal = self.parser.parse_signal(message_text)
            
            if signal:
                logger.info("Valid signal detected, executing trade...")
                success = self.trader.execute_signal(signal)
                
                if success:
                    logger.info("Signal executed successfully")
                    
                    # Send signal notification
                    if self.notification_chat_id:
                        symbol_name = signal.symbol.replace('/USDT', '')
                        direction_emoji = "🟢" if signal.direction == "BUY" else "🔴"
                        message = f"{direction_emoji} {signal.direction} {symbol_name}\nEntry: {signal.entry_price}\nLeverage: {signal.leverage}X"
                        await self.send_notification(message)
                    
                    # Check order status for achievements (will be checked periodically)
                    # The periodic_order_check task will handle this
                else:
                    logger.error("Failed to execute signal")
            else:
                logger.warning("Could not parse signal from message")
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def start_listening(self):
        """Start listening to Telegram channel."""
        await self.initialize()
        
        @self.client.on(events.NewMessage(chats=self.channel_id))
        async def new_message_handler(event):
            await self.handle_message(event)
        
        # Start periodic order checking for achievements
        if self.notification_chat_id:
            asyncio.create_task(self.periodic_order_check())
            logger.info("Order status monitoring started for achievement notifications")
        
        logger.info(f"Started listening to channel {self.channel_id}")
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        # Keep the client running
        await self.client.run_until_disconnected()
    
    async def stop(self):
        """Stop the Telegram client."""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client disconnected")


def start_web_server():
    """Start the web server in a separate thread."""
    try:
        import sys
        import importlib.util
        
        # Try to import web_server module
        web_server_path = os.path.join(os.path.dirname(__file__), 'web_server.py')
        if os.path.exists(web_server_path):
            spec = importlib.util.spec_from_file_location("web_server", web_server_path)
            web_server = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(web_server)
            port = int(os.getenv('PORT', 8000))
            web_server.start_web_server(port)
        else:
            logger.warning("web_server.py not found, skipping web server")
    except Exception as e:
        logger.warning(f"Could not start web server: {e}")


async def main():
    """Main entry point."""
    # Start web server in background thread
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    logger.info("Web server started on background thread")
    
    # Load configuration from environment
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    telegram_api_id = os.getenv('TELEGRAM_APP_ID')
    telegram_api_hash = os.getenv('TELEGRAM_API_HASH')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
    
    # Validate configuration
    if not all([api_key, api_secret, telegram_api_id, telegram_api_hash, channel_id]):
        logger.error("Missing required environment variables. Please check your .env file.")
        logger.error("Required: BINANCE_API_KEY, BINANCE_API_SECRET, TELEGRAM_APP_ID, "
                    "TELEGRAM_API_HASH, TELEGRAM_CHANNEL_ID")
        return
    
    try:
        channel_id_int = int(channel_id)
    except ValueError:
        logger.error("TELEGRAM_CHANNEL_ID must be a valid integer")
        return
    
    # Get notification chat ID (optional)
    notification_chat_id = os.getenv('TELEGRAM_NOTIFICATION_CHAT_ID')
    notification_chat_id_int = None
    if notification_chat_id:
        try:
            notification_chat_id_int = int(notification_chat_id)
            logger.info(f"Notifications will be sent to chat: {notification_chat_id_int}")
        except ValueError:
            logger.warning(f"Invalid TELEGRAM_NOTIFICATION_CHAT_ID: {notification_chat_id}")
    
    # Initialize trader first
    trader = BinanceFuturesTrader(api_key, api_secret, dry_run=dry_run)
    
    # Initialize Telegram listener
    listener = TelegramSignalListener(
        api_id=int(telegram_api_id),
        api_hash=telegram_api_hash,
        channel_id=channel_id_int,
        trader=trader,
        notification_chat_id=notification_chat_id_int
    )
    
    # Start listening
    try:
        await listener.start_listening()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except SessionPasswordNeededError as e:
        logger.error(f"Session authentication error: {e}")
        logger.error("Bot will exit. Please re-authenticate using Railway CLI shell.")
        await listener.stop()
        # Exit with error code so Railway knows to restart
        import sys
        sys.exit(1)
    except Exception as e:
        error_msg = str(e)
        # Check for connection errors
        connection_errors = [
            "ConnectionRefusedError",
            "Connection failed",
            "Connect call failed",
            "Connection to Telegram failed"
        ]
        
        if any(err in error_msg for err in connection_errors):
            logger.error("")
            logger.error("=" * 60)
            logger.error("❌ TELEGRAM CONNECTION ERROR")
            logger.error("=" * 60)
            logger.error("Cannot connect to Telegram servers.")
            logger.error("")
            logger.error("🔴 PythonAnywhere FREE accounts block outbound connections!")
            logger.error("   Upgrade to paid account OR switch to Railway/Render")
            logger.error("=" * 60)
            logger.error("")
        elif "Could not find a matching Constructor ID" in error_msg or "misusing the session" in error_msg:
            logger.error("Session corruption detected in main loop. Bot will exit.")
            logger.error("Please re-authenticate using: railway shell -> python3 trading_bot.py")
        else:
            logger.error(f"Error in main loop: {e}")
        await listener.stop()
        import sys
        sys.exit(1)
    finally:
        await listener.stop()


if __name__ == '__main__':
    asyncio.run(main())
