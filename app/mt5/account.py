import MetaTrader5 as mt5

def account_info():
    acc = mt5.account_info()
    return acc._asdict()
