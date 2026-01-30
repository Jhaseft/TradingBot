import MetaTrader5 as mt5

def positions():
    pos = mt5.positions_get()
    return [p._asdict() for p in pos] if pos else []
