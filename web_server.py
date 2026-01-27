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
                <title>Trading Bot Dashboard</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                        max-width: 1100px;
                        margin: 40px auto;
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
                        margin: 0 0 5px 0;
                    }}
                    .subtitle {{
                        color: #777;
                        margin: 0 0 15px 0;
                        font-size: 14px;
                    }}
                    .status-banner {{
                        padding: 12px 16px;
                        background: #4CAF50;
                        color: white;
                        border-radius: 5px;
                        margin: 10px 0 20px 0;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        font-size: 14px;
                    }}
                    .status-row {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 15px;
                        margin: 0 0 20px 0;
                    }}
                    .status-card {{
                        flex: 1 1 180px;
                        min-width: 180px;
                        background: #f9f9f9;
                        border-radius: 8px;
                        padding: 10px 12px;
                        border-left: 4px solid #4CAF50;
                    }}
                    .status-card h3 {{
                        margin: 0 0 4px 0;
                        font-size: 12px;
                        text-transform: uppercase;
                        letter-spacing: .04em;
                        color: #555;
                    }}
                    .status-card p {{
                        margin: 0;
                        font-size: 13px;
                        font-weight: 600;
                        color: #222;
                    }}
                    .status-card.danger {{
                        border-left-color: #f44336;
                    }}
                    .layout {{
                        display: grid;
                        grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.9fr);
                        gap: 20px;
                        margin-top: 10px;
                    }}
                    @media (max-width: 900px) {{
                        .layout {{
                            grid-template-columns: 1fr;
                        }}
                    }}
                    .info {{
                        background: #f9f9f9;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 0;
                    }}
                    .info ul {{
                        margin: 8px 0 0 16px;
                    }}
                    .info li {{
                        margin-bottom: 4px;
                        font-size: 14px;
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
                        margin: 10px 0 0 0;
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
                        padding: 8px 16px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 13px;
                        margin: 6px 6px 6px 0;
                    }}
                    .refresh-btn:hover {{
                        background: #45a049;
                    }}
                    .filter-btn {{
                        background: #e0e0e0;
                        color: #333;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                        margin: 2px 3px;
                    }}
                    .filter-btn.active {{
                        background: #4CAF50;
                        color: white;
                    }}
                    .auto-refresh {{
                        margin: 6px 0;
                        font-size: 12px;
                    }}
                </style>
                <script>
                    let currentFilter = 'all';
                    let lastSignal = '-';
                    let lastTrade = '-';
                    let lastTP = '-';
                    let lastError = '-';

                    function shorten(line) {{
                        if (!line || line === '-') return '-';
                        if (line.length <= 130) return line;
                        return line.slice(0, 130) + '…';
                    }}

                    function loadLogs() {{
                        fetch('/logs.json')
                            .then(response => response.json())
                            .then(data => {{
                                const logsContainer = document.getElementById('logs');
                                logsContainer.innerHTML = '';
                                lastSignal = '-';
                                lastTrade = '-';
                                lastTP = '-';
                                lastError = '-';

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

                                    // Tag type for filtering
                                    if (log.includes('[SIGNAL]')) {{
                                        entry.dataset.type = 'signal';
                                        lastSignal = log;
                                    }} else if (log.includes('[TRADE]')) {{
                                        entry.dataset.type = 'trade';
                                        lastTrade = log;
                                    }} else if (log.includes('[TP]')) {{
                                        entry.dataset.type = 'tp';
                                        lastTP = log;
                                    }} else if (log.includes('ERROR')) {{
                                        entry.dataset.type = 'error';
                                        lastError = log;
                                    }} else {{
                                        entry.dataset.type = 'info';
                                    }}

                                    entry.textContent = log;
                                    if (
                                        currentFilter === 'all' ||
                                        entry.dataset.type === currentFilter ||
                                        (currentFilter === 'signal_trade' &&
                                         (entry.dataset.type === 'signal' || entry.dataset.type === 'trade'))
                                    ) {{
                                        logsContainer.appendChild(entry);
                                    }}
                                }});

                                // Update summary cards
                                document.getElementById('lastSignal').textContent = shorten(lastSignal);
                                document.getElementById('lastTrade').textContent = shorten(lastTrade);
                                document.getElementById('lastTP').textContent = shorten(lastTP);
                                document.getElementById('lastError').textContent = shorten(lastError);

                                // Auto-scroll to bottom
                                logsContainer.scrollTop = logsContainer.scrollHeight;
                            }})
                            .catch(err => {{
                                console.error('Error loading logs:', err);
                            }});
                    }}
                    
                    // Auto-refresh logs every 4 seconds
                    let autoRefreshInterval;
                    function toggleAutoRefresh() {{
                        const checkbox = document.getElementById('autoRefresh');
                        if (checkbox.checked) {{
                            autoRefreshInterval = setInterval(loadLogs, 4000);
                        }} else {{
                            clearInterval(autoRefreshInterval);
                        }}
                    }}

                    function setFilter(filter) {{
                        currentFilter = filter;
                        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
                        const btn = document.getElementById('filter-' + filter);
                        if (btn) btn.classList.add('active');
                        loadLogs();
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
                    <h1>🤖 Trading Bot Dashboard</h1>
                    <p class="subtitle">Status, recent signals, trades and live logs.</p>

                    <div class="status-banner">
                        <span>✅ Bot is running and monitoring Telegram channel</span>
                        <span>Mode: <strong>{'DRY RUN' if dry_run.lower() == 'true' else 'LIVE'}</strong></span>
                    </div>

                    <div class="status-row">
                        <div class="status-card">
                            <h3>Channel</h3>
                            <p>{channel_id}</p>
                        </div>
                        <div class="status-card">
                            <h3>Last signal</h3>
                            <p id="lastSignal">-</p>
                        </div>
                        <div class="status-card">
                            <h3>Last trade</h3>
                            <p id="lastTrade">-</p>
                        </div>
                        <div class="status-card">
                            <h3>Last TP / Profit</h3>
                            <p id="lastTP">-</p>
                        </div>
                        <div class="status-card danger">
                            <h3>Last error</h3>
                            <p id="lastError">-</p>
                        </div>
                    </div>

                    <div class="layout">
                        <div class="info">
                            <h3>ℹ️ Overview</h3>
                            <ul>
                                <li>Monitors a Telegram channel for trading signals.</li>
                                <li>Parses direction, symbol, leverage, entry and targets.</li>
                                <li>Executes futures trades on Binance (LIVE when DRY_RUN=false).</li>
                                <li>Sets stop loss at -170% ROI and a single TP (100% position) at first target.</li>
                                <li>Optionally sends Telegram notifications to your private chat.</li>
                            </ul>
                            <p style="font-size: 12px; color: #777; margin-top: 10px;">
                                Use the filters on the right to focus on signals & trades or only errors.
                            </p>
                        </div>

                        <div class="info">
                            <h3>📊 Live Logs</h3>
                            <div style="margin: 4px 0 8px 0; display:flex; flex-wrap:wrap; align-items:center;">
                                <button class="refresh-btn" onclick="loadLogs()">🔄 Refresh Logs</button>
                                <label class="auto-refresh" style="margin-left:10px;">
                                    <input type="checkbox" id="autoRefresh" onchange="toggleAutoRefresh()" checked>
                                    Auto-refresh (4s)
                                </label>
                                <div style="margin-left:auto; font-size:12px;">
                                    <button id="filter-all" class="filter-btn active" onclick="setFilter('all')">All</button>
                                    <button id="filter-signal_trade" class="filter-btn" onclick="setFilter('signal_trade')">Signals & Trades</button>
                                    <button id="filter-error" class="filter-btn" onclick="setFilter('error')">Errors</button>
                                </div>
                            </div>
                            <div id="logs" class="logs-container">
                                <div class="log-entry log-info">Loading logs...</div>
                            </div>
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


def start_web_server(port=8080):
    """Start the web server on the specified port."""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Web server started on port {port}")
    server.serve_forever()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    start_web_server(port)
