import MetaTrader5 as mt5

def buy(symbol: str, lot: float):
    tick = mt5.symbol_info_tick(symbol)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": tick.ask,
        "deviation": 20,
        "magic": 999001,
        "comment": "python-local",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    return mt5.order_send(request)._asdict()
