from fastapi import APIRouter, Request
from datetime import datetime
from app.services.storage import save_data, broadcast

router = APIRouter()

@router.post("/webhook")
async def tradingview_webhook(request: Request):
    data = await request.json()
    now = datetime.now()
    save_data(data, now)
    await broadcast(data, now)
    return {"status": "ok"}
