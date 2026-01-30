import MetaTrader5 as mt5

def symbols():
    return [s.name for s in mt5.symbols_get()]
