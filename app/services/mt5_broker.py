import MetaTrader5 as mt5
import requests
import mysql.connector

EVOLUTION_URL = "https://automatizando-evolution-api-last.pk1ooa.easypanel.host"
INSTANCE = "darwin"
API_KEY = "B33A4273FDE5-4CE9-A87B-16AB8B1A7FB6"

NUMBERS = [
    "59160761264",
    "59163427591",
    "59174048209",
]

def save_trade_to_db(result, symbol, volume, price, sl, tp):
    conexion = mysql.connector.connect(
        host="206.183.130.17",
        user="Meta5",
        password="Meta51",
        database="Meta5",
        port=7701
    )

    cursor = conexion.cursor()

    # Calcular diferencias
    diff_sl = price - sl if sl is not None else None
    diff_tp = tp - price if tp is not None else None

    sql = """
        INSERT INTO operaciones_mt5
        (ticket, symbol, type, volume, price_open, stop_loss, take_profit, magic_number, retcode, diff_sl, diff_tp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    valores = (
        result.order,
        symbol,
        "BUY",
        volume,
        price,
        sl,
        tp,
        10001,
        result.retcode,
        diff_sl,
        diff_tp
    )

    cursor.execute(sql, valores)
    conexion.commit()
    conexion.close()

def send_whatsapp_message(text):
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"

    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    for number in NUMBERS:
        payload = {
            "number": number,
            "text": text
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"📩 Mensaje enviado a {number} | Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error enviando mensaje a {number}: {e}")

def init_mt5():
    if mt5.initialize():
        return

    err = mt5.last_error()
    raise RuntimeError(f"MT5 no pudo inicializarse: {err}")


def open_trade(symbol, sl=None, tp=None, volume=None):
    init_mt5()

    # ==============================
    #  VERIFICAR SÍMBOLO
    # ==============================
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        raise RuntimeError(f"Símbolo no encontrado: {symbol}")

    if not symbol_info.visible:
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"No se pudo seleccionar el símbolo: {symbol}")

    # ==============================
    #  VALIDAR VOLUMEN
    # ==============================
    
    volume_min = symbol_info.volume_min
    volume_max = symbol_info.volume_max
    volume_step = symbol_info.volume_step

    if volume is None:
        volume = volume_min  # usar mínimo si no se envía

    volume = float(volume)

    # Ajustar al step permitido por broker
    volume = round(volume / volume_step) * volume_step
    volume = max(volume_min, min(volume, volume_max))

    if volume < volume_min:
        raise RuntimeError("Volumen menor al mínimo permitido por el broker")

    print(f"Volumen final usado: {volume}")

    # ==============================
    #  FIN VOLUMEN
    # ==============================

    # --- Obtener precio actual ---
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        raise RuntimeError(f"No se pudo obtener tick para {symbol}")

    price = tick.ask  # BUY usa ASK
    digits = symbol_info.digits
    point = symbol_info.point
    stops_level = symbol_info.trade_stops_level

    # --- Normalizar SL / TP ---
    if sl is not None:
        sl = round(float(sl), digits)

    if tp is not None:
        tp = round(float(tp), digits)

    min_distance = stops_level * point

    # --- Validaciones BUY ---
    if sl is not None:
        if sl >= price:
            raise RuntimeError("SL debe estar DEBAJO del precio en BUY")
        if (price - sl) < min_distance:
            raise RuntimeError("SL demasiado cerca del precio (stops_level)")

    if tp is not None:
        if tp <= price:
            raise RuntimeError("TP debe estar ENCIMA del precio en BUY")
        if (tp - price) < min_distance:
            raise RuntimeError("TP demasiado cerca del precio (stops_level)")

    # --- Crear request ---
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "deviation": 20,
        "magic": 10001,
        "comment": "TV Auto Buy",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    if sl is not None:
        request["sl"] = sl

    if tp is not None:
        request["tp"] = tp

    message = f"""
    🚀 NUEVA SEÑAL DE COMPRA

    📊 Símbolo: {symbol}
    💰 Precio actual: {price}
    📦 Volumen: {volume}

    🛑 Stop Loss: {sl if sl else 'No definido'}
    🎯 Take Profit: {tp if tp else 'No definido'}

    ⚡ Se ejecutará orden BUY ahora...
    """
    send_whatsapp_message(message)

    print("📤 Enviando orden BUY:", request)

    result = mt5.order_send(request)

    if result is None:
        raise RuntimeError(f"Error MT5: {mt5.last_error()}")

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise RuntimeError(
            f"MT5 rechazó la orden: {result.comment} | retcode={result.retcode}"
        )

    save_trade_to_db(result, symbol, volume, price, sl, tp)
    print(f"✅ BUY ejecutado correctamente | Ticket: {result.order}")

    return result