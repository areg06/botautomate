#!/usr/bin/env python3
"""
Telegram Signal Trading Bot for Binance Futures
Monitors Telegram channel for trading signals and executes trades automatically.
"""

import os
import re
import asyncio
import logging
from typing import Optional, Dict, List
from decimal import Decimal, ROUND_DOWN
from dataclasses import dataclass
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
import ccxt
from ccxt.base.errors import InsufficientFunds, NetworkError, ExchangeError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
                targets=targets[:3]  # Only take first 3 targets
            )
            
            logger.info(f"Parsed signal: {signal.direction} {signal.symbol} @ {signal.entry_price} "
                       f"with {signal.leverage}X leverage, {len(signal.targets)} targets")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error parsing signal: {e}")
            return None


class BinanceFuturesTrader:
    """Handles trading operations on Binance Futures using CCXT."""
    
    def __init__(self, api_key: str, api_secret: str, dry_run: bool = False):
        """
        Initialize Binance Futures trader.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            dry_run: If True, only print actions without executing
        """
        self.dry_run = dry_run
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # Use futures
            },
            'sandbox': dry_run,  # Use testnet if dry run
        })
        
        if dry_run:
            logger.info("DRY RUN MODE: No actual trades will be executed")
        else:
            logger.info("LIVE MODE: Trades will be executed on Binance Futures")
    
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
            self.exchange.set_leverage(leverage, symbol)
            logger.info(f"Set leverage to {leverage}X for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting leverage: {e}")
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
        
        Args:
            balance: Available USDT balance
            entry_price: Entry price
            leverage: Leverage multiplier
        
        Returns:
            Position size in base currency
        """
        # Use 95% of balance to leave some margin
        usable_balance = balance * 0.95
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
            
            order = self.exchange.create_market_order(
                symbol=signal.symbol,
                side=side,
                amount=position_size
            )
            
            logger.info(f"Placed {side} market order: {order.get('id')} "
                       f"for {position_size} {signal.symbol}")
            return order.get('id')
            
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
    
    def place_take_profit_order(self, signal: TradingSignal, target_price: float, 
                                position_size: float, order_num: int) -> Optional[str]:
        """
        Place a take profit limit order.
        
        Args:
            signal: Trading signal
            target_price: Target price for take profit
            position_size: Position size to close (33% of total)
            order_num: Order number (1, 2, or 3)
        
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
            
            order = self.exchange.create_limit_order(
                symbol=signal.symbol,
                side=side,
                amount=position_size,
                price=target_price
            )
            
            logger.info(f"Placed take profit {order_num}: {order.get('id')} "
                       f"for {position_size} {signal.symbol} @ {target_price}")
            return order.get('id')
            
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
            
            # Step 5: Place take profit orders (33% each for first 3 targets)
            target_size = position_size / 3.0
            target_size = float(Decimal(str(target_size)).quantize(Decimal('0.001'), rounding=ROUND_DOWN))
            
            tp_orders = []
            for i, target_price in enumerate(signal.targets[:3], 1):
                tp_order_id = self.place_take_profit_order(
                    signal, target_price, target_size, i
                )
                if tp_order_id:
                    tp_orders.append(tp_order_id)
                else:
                    logger.warning(f"Failed to place take profit order {i}")
            
            logger.info(f"Successfully executed signal: Entry order {entry_order_id}, "
                       f"{len(tp_orders)} take profit orders placed")
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return False


class TelegramSignalListener:
    """Listens to Telegram channel for trading signals."""
    
    def __init__(self, api_id: int, api_hash: str, channel_id: int, 
                 trader: BinanceFuturesTrader):
        """
        Initialize Telegram listener.
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API hash
            channel_id: Channel ID to monitor
            trader: BinanceFuturesTrader instance
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.channel_id = channel_id
        self.trader = trader
        self.parser = SignalParser()
        self.client = None
    
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
            
            await self.client.start()
            
            # Check if password is needed
            if not await self.client.is_user_authorized():
                if not is_interactive:
                    logger.error("=" * 60)
                    logger.error("TELEGRAM AUTHENTICATION REQUIRED")
                    logger.error("=" * 60)
                    logger.error("Please use Railway's web shell to authenticate:")
                    logger.error("1. Go to Railway dashboard → Your deployment")
                    logger.error("2. Click 'View Logs' → Click 'Open Shell' button")
                    logger.error("3. Run: python3 trading_bot.py")
                    logger.error("4. Enter your phone number and verification code")
                    logger.error("5. Session will be saved automatically")
                    logger.error("=" * 60)
                raise SessionPasswordNeededError("2FA password required")
            
            logger.info("Telegram client initialized successfully")
        except SessionPasswordNeededError:
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Telegram client: {e}")
            logger.info("If this is first run, you need to authenticate interactively.")
            raise
    
    async def handle_message(self, event):
        """Handle incoming message from Telegram channel."""
        try:
            message_text = event.message.message
            
            # Check if message contains trading signal indicators
            if '🟢 Long' not in message_text and '🔴 Short' not in message_text:
                return
            
            logger.info(f"Received potential signal message from channel {self.channel_id}")
            logger.debug(f"Message content: {message_text[:200]}...")
            
            # Parse signal
            signal = self.parser.parse_signal(message_text)
            
            if signal:
                logger.info("Valid signal detected, executing trade...")
                success = self.trader.execute_signal(signal)
                
                if success:
                    logger.info("Signal executed successfully")
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
        
        logger.info(f"Started listening to channel {self.channel_id}")
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        # Keep the client running
        await self.client.run_until_disconnected()
    
    async def stop(self):
        """Stop the Telegram client."""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client disconnected")


async def main():
    """Main entry point."""
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
    
    # Initialize trader
    trader = BinanceFuturesTrader(api_key, api_secret, dry_run=dry_run)
    
    # Initialize Telegram listener
    listener = TelegramSignalListener(
        api_id=int(telegram_api_id),
        api_hash=telegram_api_hash,
        channel_id=channel_id_int,
        trader=trader
    )
    
    # Start listening
    try:
        await listener.start_listening()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        await listener.stop()


if __name__ == '__main__':
    asyncio.run(main())
