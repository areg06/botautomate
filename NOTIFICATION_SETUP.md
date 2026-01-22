# Notification Setup Guide

The bot can forward signals and send achievement notifications to your personal Telegram chat.

## Features

1. **Forward Signals**: Automatically forwards detected signals to your chat
2. **Achievement Notifications**: Sends notifications when targets are hit:
   ```
   💸 GALA/USDT
   ✅ Target #1 Done
   Current profit: 75.0%
   ```

## How to Get Your Chat ID

### Method 1: Using @userinfobot (Easiest)

1. Open Telegram
2. Search for `@userinfobot`
3. Start a conversation with the bot
4. Send any message (e.g., `/start`)
5. The bot will reply with your user information
6. Look for **"Id"** - that's your chat ID (e.g., `556232999`)

### Method 2: Using @RawDataBot

1. Open Telegram
2. Search for `@RawDataBot`
3. Start a conversation
4. Send `/start`
5. The bot will send your raw data
6. Look for `"id": 556232999` - that's your chat ID

### Method 3: From Forwarded Message JSON

If you have a forwarded message JSON (like you showed), the chat ID is in:
```json
"chat": {
  "id": 556232999,  // This is your chat ID
  ...
}
```

## Setup

### 1. Add to .env File

Add this line to your `.env` file:

```bash
TELEGRAM_NOTIFICATION_CHAT_ID=556232999
```

Replace `556232999` with your actual chat ID.

### 2. Restart the Bot

After adding the chat ID, restart the bot:

```bash
# If running manually
python3 trading_bot.py

# If running as service
sudo systemctl restart trading-bot
```

## What You'll Receive

### When Signal is Detected:
- **Forwarded message**: The original signal message from the channel
- **Summary notification**: Quick summary with direction, symbol, entry, leverage

### When Target is Hit:
```
💸 GALA/USDT
✅ Target #1 Done
Current profit: 75.0%
```

The bot checks order status every 30 seconds and sends notifications when targets are achieved.

## Troubleshooting

### Not receiving notifications?
- Check that `TELEGRAM_NOTIFICATION_CHAT_ID` is set correctly
- Make sure the chat ID is a number (no quotes)
- Verify the bot has permission to send messages to you
- Check bot logs: `sudo journalctl -u trading-bot -f`

### Chat ID not working?
- Make sure you've started a conversation with the bot first
- Try sending a message to yourself and check the ID
- For group chats, use the group's chat ID (negative number)

### Notifications delayed?
- The bot checks order status every 30 seconds
- Binance API may have slight delays in order status updates
- This is normal and expected

## Example .env Configuration

```bash
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
TELEGRAM_APP_ID=your_app_id
TELEGRAM_API_HASH=your_hash
TELEGRAM_CHANNEL_ID=-1002299206473
TELEGRAM_NOTIFICATION_CHAT_ID=556232999
DRY_RUN=false
```

## Notes

- Notifications are optional - if `TELEGRAM_NOTIFICATION_CHAT_ID` is not set, the bot will work normally without notifications
- The bot forwards the original signal message, so you get the full context
- Achievement notifications are sent automatically when orders are filled
- Profit percentage is calculated based on leverage and price movement
