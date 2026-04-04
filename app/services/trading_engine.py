from app.services.mt5_broker import open_trade

ACTIVE_TRADES = {}


def calculate_btc_trade(entry_price, sl_price, capital, risk_percent=0.10, rr=5):
    """
    BTCUSD:
    - Riesgo fijo %
    - Lote dinámico según distancia al SL
    - TP automático RR 1:5
    """

    riesgo = capital * risk_percent
    stop_distance = abs(entry_price - sl_price)

    if stop_distance == 0:
        return None

    lotaje = riesgo / stop_distance
    tp_distance = stop_distance * rr
    tp_price = entry_price + tp_distance  # SOLO BUY

    return {
        "lotaje": round(lotaje, 3),
        "tp_price": round(tp_price, 2),
        "stop_distance": round(stop_distance, 2),
    }


def select_best_row(rows):
    if not rows:
        return None

    positive_rows = [r for r in rows if r.get("pnl_percent", 0) > 0]

    if not positive_rows:
        print("No hay filas con PnL positivo")
        return None

    return sorted(
        positive_rows,
        key=lambda x: (x.get("pnl_percent", 0), x.get("winrate", 0)),
        reverse=True
    )[0]


def handle_signal(data):

    print("Recibiendo señal:", data)

    symbol = data.get("symbol")
    if symbol != "BTCUSD":
        print("Solo operamos BTCUSD")
        return

    rows = data.get("data", [])
    best_row = select_best_row(rows)

    if not best_row:
        print("No hay configuración rentable, no operamos")
        return

    entry_price = float(data["entry_price"])
    sl = float(best_row["sl_price"])
    capital = float(data["capital"])

    trade_calc = calculate_btc_trade(
        entry_price=entry_price,
        sl_price=sl,
        capital=capital,
        risk_percent=0.10,
        rr=5
    )

    if not trade_calc:
        print("Error en cálculo")
        return

    volume = trade_calc["lotaje"]
    tp = trade_calc["tp_price"]

    print(f"Entry: {entry_price}")
    print(f"SL: {sl}")
    print(f"TP (1:5): {tp}")
    print(f"Volumen dinámico: {volume}")

    try:
        print(f"Abriendo BUY en {symbol}")

        result = open_trade(
            symbol=symbol,
            sl=sl,
            tp=tp,
            volume=volume
        )

        ticket = getattr(result, "order", None)
        ACTIVE_TRADES[symbol] = ticket

        print(f"Trade abierto ID: {ticket}")

    except Exception as e:
        print(f"Error abriendo trade: {e}")