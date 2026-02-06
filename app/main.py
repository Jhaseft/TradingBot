from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import webhook, dashboard

app = FastAPI(title="TradingView Dashboard")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(webhook.router)
app.include_router(dashboard.router)
