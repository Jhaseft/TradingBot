import MetaTrader5 as mt5


# =========================
# INIT MT5 (solo si no está iniciado)
# =========================
def init_mt5():
    if mt5.initialize():
        return

    err = mt5.last_error()
    raise RuntimeError(f"MT5 no pudo inicializarse: {err}")



def open_trade(symbol, side, volume, sl=None, tp=None):
    init_mt5()

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        raise RuntimeError(f"Símbolo no encontrado: {symbol}")

    if not symbol_info.visible:
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"No se pudo seleccionar el símbolo: {symbol}")

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        raise RuntimeError(f"No se pudo obtener tick para {symbol}")

    price = tick.ask if side == "BUY" else tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "deviation": 20,
        "magic": 10001,
        "comment": "TradingView Auto",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # ✅ Solo agregar SL y TP si existen
    if sl is not None:
        request["sl"] = float(sl)

    if tp is not None:
        request["tp"] = float(tp)

    print("Enviando orden:", request)

    result = mt5.order_send(request)

    if result is None:
        raise RuntimeError(f"Error MT5: {mt5.last_error()}")

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise RuntimeError(f"MT5 rechazó la orden: {result.comment} | retcode={result.retcode}")

    print(f"✅ Orden ejecutada correctamente | Ticket: {result.order}")

    return result



def close_trade(position_id):
    init_mt5()

    positions = mt5.positions_get(ticket=position_id)
    if not positions:
        raise RuntimeError(f"No se encontró posición con ID {position_id}")

    pos = positions[0]

    symbol = pos.symbol
    volume = pos.volume

    side = (
        mt5.ORDER_TYPE_SELL
        if pos.type == mt5.POSITION_TYPE_BUY
        else mt5.ORDER_TYPE_BUY
    )

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        raise RuntimeError(f"No se pudo obtener tick para {symbol}")

    price = tick.bid if side == mt5.ORDER_TYPE_SELL else tick.ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": position_id,
        "symbol": symbol,
        "volume": volume,
        "type": side,
        "price": price,
        "deviation": 20,
        "magic": 10001,
        "comment": "Auto Close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    print("Enviando cierre:", request)

    result = mt5.order_send(request)

    if result is None:
        raise RuntimeError(f"Error MT5 al cerrar: {mt5.last_error()}")

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise RuntimeError(f"MT5 rechazó el cierre: {result.comment}")

    print(f"✅ Posición cerrada correctamente | Ticket: {result.order}")

    return result
