"""
Shared state between the trading bot and the FastAPI dashboard.

Lightweight JSON-based store, safe to use from both the bot and dashboard_server.py.
"""

import json
import os
import threading
from datetime import datetime
from typing import Any, Dict, List

BASE_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(BASE_DIR, "dashboard_state.json")
_LOCK = threading.Lock()

DEFAULT_STATE: Dict[str, Any] = {
    "mode": "DRY RUN",
    "channel_id": "Not set",
    "last_signal": None,
    "last_trade": None,
    "last_tp": None,
    "last_error": None,
    "uptime_started_at": None,
    "logs": [],  # list of {ts, level, tag, message}
    "max_logs": 500,
}


def _load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_FILE):
        return DEFAULT_STATE.copy()
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in DEFAULT_STATE.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return DEFAULT_STATE.copy()


def _save_state(state: Dict[str, Any]) -> None:
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_FILE)


def get_state() -> Dict[str, Any]:
    """Return a copy of the current dashboard state."""
    with _LOCK:
        return _load_state()


def update_status(mode: str, channel_id: str) -> None:
    """Update operation mode and source channel ID."""
    with _LOCK:
        state = _load_state()
        state["mode"] = mode
        state["channel_id"] = channel_id
        if not state["uptime_started_at"]:
            state["uptime_started_at"] = datetime.utcnow().isoformat()
        _save_state(state)


def record_signal(symbol: str, direction: str) -> None:
    with _LOCK:
        state = _load_state()
        state["last_signal"] = {
            "symbol": symbol,
            "direction": direction,
            "ts": datetime.utcnow().isoformat(),
        }
        _save_state(state)


def record_trade(symbol: str, direction: str, entry_price: float, qty: float) -> None:
    with _LOCK:
        state = _load_state()
        state["last_trade"] = {
            "symbol": symbol,
            "direction": direction,
            "entry_price": float(entry_price),
            "qty": float(qty),
            "ts": datetime.utcnow().isoformat(),
        }
        _save_state(state)


def record_tp(symbol: str, roi_pct: float) -> None:
    with _LOCK:
        state = _load_state()
        state["last_tp"] = {
            "symbol": symbol,
            "roi_pct": float(roi_pct),
            "ts": datetime.utcnow().isoformat(),
        }
        _save_state(state)


def record_error(message: str) -> None:
    with _LOCK:
        state = _load_state()
        state["last_error"] = {
            "message": message,
            "ts": datetime.utcnow().isoformat(),
        }
        _save_state(state)


def append_log(level: str, tag: str, message: str) -> None:
    """Append a log entry to the dashboard state."""
    with _LOCK:
        state = _load_state()
        logs: List[Dict[str, Any]] = state.get("logs", [])
        logs.append(
            {
                "ts": datetime.utcnow().isoformat(),
                "level": level,
                "tag": tag,
                "message": message,
            }
        )
        max_logs = state.get("max_logs", 500)
        if len(logs) > max_logs:
            logs = logs[-max_logs:]
        state["logs"] = logs
        _save_state(state)

