#!/bin/bash
# Run this on the VPS (e.g. in ~/botautomate) to create systemd service files.
# Usage: bash vps-create-services.sh   (or: chmod +x vps-create-services.sh && ./vps-create-services.sh)

set -e

BOT_SVC="/etc/systemd/system/trading-bot.service"
DASH_SVC="/etc/systemd/system/trading-dashboard.service"

# Adjust if your project is not in /root/botautomate
BASE="/root/botautomate"
VENV="${BASE}/venv"

echo "Creating ${BOT_SVC} ..."
sudo tee "$BOT_SVC" << EOF
[Unit]
Description=Telegram Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${BASE}
Environment="PATH=${VENV}/bin"
ExecStart=${VENV}/bin/python3 trading_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Creating ${DASH_SVC} ..."
sudo tee "$DASH_SVC" << EOF
[Unit]
Description=Trading Bot Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${BASE}
Environment="PATH=${VENV}/bin"
Environment="DASHBOARD_PORT=4000"
ExecStart=${VENV}/bin/python3 dashboard_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Done. Start with:"
echo "  sudo systemctl start trading-bot"
echo "  sudo systemctl start trading-dashboard"
echo "  sudo systemctl enable trading-bot"
echo "  sudo systemctl enable trading-dashboard"
