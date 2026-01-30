import MetaTrader5 as mt5
from app.core.logger import logger

def connect_mt5():
    if not mt5.initialize():
        raise RuntimeError(f"MT5 error: {mt5.last_error()}")

    account = mt5.account_info()
    logger.info(f"Conectado a MT5 | Cuenta: {account.login}")
    return True
