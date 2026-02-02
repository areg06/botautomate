import os
import json
import asyncio
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from dashboard_state import get_state, get_balance_percent, set_balance_percent

BASE_DIR = os.path.dirname(__file__)
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = FastAPI(title="Trading Bot Dashboard")

if os.path.isdir(os.path.join(BASE_DIR, "static")):
    app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    state = get_state()
    uptime_str = "-"
    started_at = state.get("uptime_started_at")
    if started_at:
        try:
            dt = datetime.fromisoformat(started_at)
            delta = datetime.utcnow() - dt
            hours = int(delta.total_seconds() // 3600)
            mins = int((delta.total_seconds() % 3600) // 60)
            uptime_str = f"{hours}h {mins}m"
        except Exception:
            pass

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "mode": state.get("mode", "DRY RUN"),
            "channel_id": state.get("channel_id", "Not set"),
            "uptime": uptime_str,
            "balance_percent": state.get("balance_percent", 15),
        },
    )


def _format_uptime(started_at):  # str | None -> str
    if not started_at:
        return "—"
    try:
        dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.utcnow()
        delta = now - dt
        total = int(delta.total_seconds())
        if total < 0:
            return "—"
        h, r = divmod(total, 3600)
        m, s = divmod(r, 60)
        if h > 0:
            return f"{h}h {m}m"
        if m > 0:
            return f"{m}m {s}s"
        return f"{s}s"
    except Exception:
        return "—"


@app.get("/api/state")
async def api_state():
    state = get_state()
    started_at = state.get("uptime_started_at")
    return {
        "mode": state.get("mode", "DRY RUN"),
        "channel_id": state.get("channel_id", "Not set"),
        "last_signal": state.get("last_signal"),
        "last_trade": state.get("last_trade"),
        "last_tp": state.get("last_tp"),
        "last_error": state.get("last_error"),
        "uptime_started_at": started_at,
        "uptime": _format_uptime(started_at),
        "balance_percent": state.get("balance_percent", 15),
    }


@app.get("/api/config")
async def get_config():
    return {"balance_percent": get_balance_percent()}


@app.post("/api/config")
async def post_config(request: Request):
    try:
        body = await request.json()
        percent = body.get("balance_percent")
        if percent is None:
            return {"ok": False, "error": "balance_percent required"}
        p = float(percent)
        p = max(1.0, min(100.0, p))
        set_balance_percent(p)
        return {"ok": True, "balance_percent": p}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/logs/stream")
async def logs_stream():
    async def event_generator():
        last_index = 0
        while True:
            state = get_state()
            logs = state.get("logs", [])
            if last_index < len(logs):
                for log in logs[last_index:]:
                    yield f"data: {json.dumps(log)}\n\n"
                last_index = len(logs)
            await asyncio.sleep(1.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "dashboard_server:app",
        host="0.0.0.0",
        port=int(os.getenv("DASHBOARD_PORT", "4000")),
        reload=False,
    )

