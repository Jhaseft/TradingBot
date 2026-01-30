from fastapi import APIRouter, WebSocket
import MetaTrader5 as mt5
import asyncio

ws_router = APIRouter()

@ws_router.websocket("/ws/ticks")
async def ticks(ws: WebSocket):
    await ws.accept()

    symbol = "EURUSD"
    mt5.symbol_select(symbol, True)

    while True:
        tick = mt5.symbol_info_tick(symbol)
        await ws.send_json({
            "symbol": symbol,
            "bid": tick.bid,
            "ask": tick.ask
        })
        await asyncio.sleep(0.5)
