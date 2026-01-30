from fastapi import APIRouter
from app.mt5.market import get_candles
from app.mt5.trading import buy
from app.mt5.account import account_info
from app.mt5.positions import positions

router = APIRouter()

@router.get("/account")
def account():
    return account_info()

@router.get("/positions")
def open_positions():
    return positions()

@router.get("/candles")
def candles(symbol: str, tf: int, limit: int = 100):
    return get_candles(symbol, tf, limit)

@router.post("/buy")
def buy_order(symbol: str, lot: float):
    return buy(symbol, lot)
