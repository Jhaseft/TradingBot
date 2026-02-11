from app.services.mt5_broker import open_trade, close_trade

ACTIVE_TRADES = {}

def handle_signal(data):
    print("Recibiendo señal:", data)

    # Solo extraemos lo mínimo necesario
    symbol = data.get("symbol")
    print(f"Símbolo extraído: {symbol}")
    volume = 0.01  # fijo por ahora
    sl = None
    tp = None

    # Decidimos la señal en base a tu 'strategy' o evento
    event = data.get("event", "").lower()
    print(f"Evento extraído: {event}")
    strategy = data.get("strategy", "").lower()
    print(f"Estrategia extraída: {strategy}")

    # Simple heurística para LONG/SHORT/CLOSE según tu info del webhook
    if "long" in strategy:
        signal = "LONG"
    elif "short" in strategy:
        signal = "SHORT"
    elif "close" in strategy or event == "close_position":
        signal = "CLOSE"
    else:
        signal = None

    if not symbol or not signal:
        print("No hay símbolo o señal válida, no hacemos nada")
        return

    try:
        # LONG
        if signal == "LONG" and symbol not in ACTIVE_TRADES:
            print(f"Intentando abrir LONG en {symbol} con volumen {volume}")
            result = open_trade(symbol, "BUY", volume, sl, tp)
            ACTIVE_TRADES[symbol] = getattr(result, "order", None)
            print(f"LONG abierto, order ID: {ACTIVE_TRADES[symbol]}")

        # SHORT
        elif signal == "SHORT" and symbol not in ACTIVE_TRADES:
            print(f"Intentando abrir SHORT en {symbol} con volumen {volume}")
            result = open_trade(symbol, "SELL", volume, sl, tp)
            ACTIVE_TRADES[symbol] = getattr(result, "order", None)
            print(f"SHORT abierto, order ID: {ACTIVE_TRADES[symbol]}")

        # CLOSE
        elif signal == "CLOSE" and symbol in ACTIVE_TRADES:
            print(f"Intentando cerrar posición en {symbol}, order ID: {ACTIVE_TRADES[symbol]}")
            close_trade(ACTIVE_TRADES[symbol])
            del ACTIVE_TRADES[symbol]
            print(f"Posición cerrada en {symbol}")

        else:
            print(f"No se ejecuta ninguna acción para la señal: {signal}")

    except Exception as e:
        print(f"Error manejando señal {signal} para {symbol}: {e}")
