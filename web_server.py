#!/usr/bin/env python3
"""
Simple web server for Railway deployment.
Provides a basic web interface and health check endpoint.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks and status page."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Trading Bot Status</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                        max-width: 800px;
                        margin: 50px auto;
                        padding: 20px;
                        background: #f5f5f5;
                    }
                    .container {
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    h1 {
                        color: #333;
                        margin-top: 0;
                    }
                    .status {
                        padding: 15px;
                        background: #4CAF50;
                        color: white;
                        border-radius: 5px;
                        margin: 20px 0;
                    }
                    .info {
                        background: #f9f9f9;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 10px 0;
                    }
                    .code {
                        background: #f4f4f4;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-family: monospace;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Trading Bot Status</h1>
                    <div class="status">
                        ✅ Bot is running and monitoring Telegram channel
                    </div>
                    <div class="info">
                        <strong>Mode:</strong> <span class="code">DRY_RUN={dry_run}</span><br>
                        <strong>Channel ID:</strong> <span class="code">{channel_id}</span><br>
                        <strong>Status:</strong> Active and listening for signals
                    </div>
                    <div class="info">
                        <h3>What this bot does:</h3>
                        <ul>
                            <li>Monitors Telegram channel for trading signals</li>
                            <li>Parses signals (direction, symbol, leverage, entry, targets)</li>
                            <li>Executes trades on Binance Futures (when DRY_RUN=false)</li>
                            <li>Places take profit orders automatically</li>
                        </ul>
                    </div>
                    <div class="info">
                        <p><strong>Note:</strong> Check Railway logs for detailed activity and signal detection.</p>
                    </div>
                </div>
            </body>
            </html>
            """.format(
                dry_run=os.getenv('DRY_RUN', 'true'),
                channel_id=os.getenv('TELEGRAM_CHANNEL_ID', 'Not set')
            )
            
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def start_web_server(port=8000):
    """Start the web server on the specified port."""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Web server started on port {port}")
    server.serve_forever()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    start_web_server(port)
