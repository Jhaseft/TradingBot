import json
from fastapi import WebSocket

LAST_DATA = None
LAST_TIME = None

connected_clients: list[WebSocket] = []

def save_data(data, timestamp):
    global LAST_DATA, LAST_TIME
    LAST_DATA = data
    LAST_TIME = timestamp

def get_data():
    return LAST_DATA, LAST_TIME

async def broadcast(data, timestamp):
    message = json.dumps({"data": data, "timestamp": str(timestamp)})
    disconnected = []
    for ws in connected_clients:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        connected_clients.remove(ws)
