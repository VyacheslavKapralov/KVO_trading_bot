from loguru import logger

from exchanges.bibit_api.connect_bybit import connect_bybit
from pybit.exceptions import InvalidRequestError


@logger.catch()
def get_balance_unified_trading(coin: str):
    count = 3
    while count > 0:
        session = connect_bybit()
        if not isinstance(session, str):
            try:
                balance = session.get_wallet_balance(accountType='UNIFIED', coin=coin)
                return round(float(balance['result']['list'][0].get('totalEquity')), 2)
            except InvalidRequestError as error:
                logger.info(f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                            f"error message: {error.message}")
                return f'Error code: {error.status_code} - {error.message}'
        count -= 1
    return f"Не удалось получить данные от биржи."


@logger.catch()
def get_balance_financing(coin: str):
    count = 3
    while count > 0:
        session = connect_bybit()
        if not isinstance(session, str):
            try:
                balance = session.get_coins_balance(accountType="FUND", coin=coin)
                return round(float(balance['result']['balance'][0].get('transferBalance')), 2)
            except InvalidRequestError as error:
                logger.info(f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                            f"error message: {error.message}")
                return f'Error code: {error.status_code} - {error.message}'
        count -= 1
    return f"Не удалось получить данные от биржи."


if __name__ == '__main__':
    logger.info('Running client_info.py from module exchange.bybit_api')
