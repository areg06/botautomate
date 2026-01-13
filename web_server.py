#!/usr/bin/env python3
"""
Simple web server for Railway deployment.
Provides a basic web interface and health check endpoint.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os
import json

# Import shared log storage
try:
    from log_storage import log_storage
except ImportError:
    # Fallback if log_storage not available
    log_storage = None

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks and status page."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/logs' or self.path == '/logs.json':
            # Return logs as JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if log_storage:
                logs = log_storage.get_logs(limit=200)
            else:
                logs = ["Log storage not available"]
            
            response = json.dumps({'logs': logs})
            self.wfile.write(response.encode())
            return
        
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Get environment variables
            dry_run = os.getenv('DRY_RUN', 'true')
            channel_id = os.getenv('TELEGRAM_CHANNEL_ID', 'Not set')
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Trading Bot Status</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                        max-width: 800px;
                        margin: 50px auto;
                        padding: 20px;
                        background: #f5f5f5;
                    }}
                    .container {{
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    h1 {{
                        color: #333;
                        margin-top: 0;
                    }}
                    .status {{
                        padding: 15px;
                        background: #4CAF50;
                        color: white;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .info {{
                        background: #f9f9f9;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 10px 0;
                    }}
                    .code {{
                        background: #f4f4f4;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-family: monospace;
                    }}
                    .logs-container {{
                        background: #1e1e1e;
                        color: #d4d4d4;
                        padding: 20px;
                        border-radius: 5px;
                        margin: 20px 0;
                        max-height: 600px;
                        overflow-y: auto;
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                        line-height: 1.5;
                    }}
                    .log-entry {{
                        margin: 2px 0;
                        padding: 2px 5px;
                        border-left: 3px solid transparent;
                    }}
                    .log-entry:hover {{
                        background: #2d2d2d;
                    }}
                    .log-info {{ border-left-color: #4CAF50; }}
                    .log-warning {{ border-left-color: #ff9800; }}
                    .log-error {{ border-left-color: #f44336; }}
                    .log-debug {{ border-left-color: #2196F3; }}
                    .refresh-btn {{
                        background: #4CAF50;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 14px;
                        margin: 10px 5px;
                    }}
                    .refresh-btn:hover {{
                        background: #45a049;
                    }}
                    .auto-refresh {{
                        margin: 10px 0;
                    }}
                </style>
                <script>
                    function loadLogs() {{
                        fetch('/logs.json')
                            .then(response => response.json())
                            .then(data => {{
                                const logsContainer = document.getElementById('logs');
                                logsContainer.innerHTML = '';
                                data.logs.forEach(log => {{
                                    const entry = document.createElement('div');
                                    entry.className = 'log-entry';
                                    // Determine log level for styling
                                    if (log.includes('ERROR')) {{
                                        entry.classList.add('log-error');
                                    }} else if (log.includes('WARNING')) {{
                                        entry.classList.add('log-warning');
                                    }} else if (log.includes('DEBUG')) {{
                                        entry.classList.add('log-debug');
                                    }} else {{
                                        entry.classList.add('log-info');
                                    }}
                                    entry.textContent = log;
                                    logsContainer.appendChild(entry);
                                }});
                                // Auto-scroll to bottom
                                logsContainer.scrollTop = logsContainer.scrollHeight;
                            }})
                            .catch(err => {{
                                console.error('Error loading logs:', err);
                            }});
                    }}
                    
                    // Auto-refresh logs every 3 seconds
                    let autoRefreshInterval;
                    function toggleAutoRefresh() {{
                        const checkbox = document.getElementById('autoRefresh');
                        if (checkbox.checked) {{
                            autoRefreshInterval = setInterval(loadLogs, 3000);
                        }} else {{
                            clearInterval(autoRefreshInterval);
                        }}
                    }}
                    
                    // Load logs on page load
                    window.onload = function() {{
                        loadLogs();
                        document.getElementById('autoRefresh').checked = true;
                        toggleAutoRefresh();
                    }};
                </script>
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
                        <h3>📊 Live Logs</h3>
                        <div style="margin: 10px 0;">
                            <button class="refresh-btn" onclick="loadLogs()">🔄 Refresh Logs</button>
                            <label class="auto-refresh">
                                <input type="checkbox" id="autoRefresh" onchange="toggleAutoRefresh()" checked>
                                Auto-refresh (3s)
                            </label>
                        </div>
                        <div id="logs" class="logs-container">
                            <div class="log-entry log-info">Loading logs...</div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
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
