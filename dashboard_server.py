import os
import json
import asyncio
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from dashboard_state import get_state

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
        },
    )


@app.get("/api/state")
async def api_state():
    state = get_state()
    return {
        "mode": state.get("mode", "DRY RUN"),
        "channel_id": state.get("channel_id", "Not set"),
        "last_signal": state.get("last_signal"),
        "last_trade": state.get("last_trade"),
        "last_tp": state.get("last_tp"),
        "last_error": state.get("last_error"),
        "uptime": state.get("uptime_started_at"),
    }


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
        port=int(os.getenv("DASHBOARD_PORT", "8080")),
        reload=False,
    )

