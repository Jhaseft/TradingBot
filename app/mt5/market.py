import MetaTrader5 as mt5

def get_candles(symbol: str, timeframe: int, limit: int = 20):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, limit)
    if rates is None:
        return []

    candles = []
    for r in rates:
        # convertir a tipos nativos Python
        candles.append({
            "time": int(r[0]),
            "open": float(r[1]),
            "high": float(r[2]),
            "low": float(r[3]),
            "close": float(r[4])
        })
    return candles
