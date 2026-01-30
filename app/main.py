from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.mt5.connection import connect_mt5
from app.api.rest import router as rest_router
from app.api.ws import ws_router

app = FastAPI(title="MT5 Python API")

# conectar MT5 al arrancar
@app.on_event("startup")
def startup():
    connect_mt5()

# montar carpeta frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# raíz "/"
@app.get("/")
def root():
    return FileResponse("frontend/index.html")

# APIs
app.include_router(rest_router, prefix="/api")
app.include_router(ws_router)
