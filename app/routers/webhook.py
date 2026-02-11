from fastapi import APIRouter, Request
from datetime import datetime
from app.services.storage import save_data, broadcast
from app.services.trading_engine import handle_signal

router = APIRouter()

@router.post("/webhook")
async def tradingview_webhook(request: Request):
    data = await request.json()
    now = datetime.now()
    save_data(data, now)
    await broadcast(data, now)
    handle_signal(data)
    return {"status": "ok"}
