from loguru import logger

from exchanges.bibit_api.connect_bybit import connect_bybit
from pybit.exceptions import InvalidRequestError


@logger.catch()
def get_instrument_info(exchange_type: str, symbol: str):
    count = 3
    while count > 0:
        session = connect_bybit()
        if not isinstance(session, str):
            try:
                return session.get_instruments_info(category=exchange_type, symbol=symbol)
            except InvalidRequestError as error:
                logger.info(f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                            f"error message: {error.message}")
                return f'Error code: {error.status_code} - {error.message}'
        count -= 1


@logger.catch()
def get_tickers(exchange_type: str, symbol: str):
    count = 3
    while count > 0:
        session = connect_bybit()
        if not isinstance(session, str):
            try:
                return session.get_tickers(category=exchange_type, symbol=symbol)
            except InvalidRequestError as error:
                logger.info(f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                            f"error message: {error.message}")
                return f'Error code: {error.status_code} - {error.message}'
        count -= 1


@logger.catch()
def get_orderbook(exchange_type: str, symbol: str):
    count = 3
    while count > 0:
        session = connect_bybit()
        if not isinstance(session, str):
            try:
                return session.get_orderbook(category=exchange_type, symbol=symbol)
            except InvalidRequestError as error:
                logger.info(f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                            f"error message: {error.message}")
                return f'Error code: {error.status_code} - {error.message}'
        count -= 1


@logger.catch()
def get_fee(exchange_type: str, symbol: str):
    count = 3
    while count > 0:
        session = connect_bybit()
        if not isinstance(session, str):
            try:
                return session.get_fee_rates(category=exchange_type, symbol=symbol)
            except InvalidRequestError as error:
                logger.info(f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                            f"error message: {error.message}")
                return f'Error code: {error.status_code} - {error.message}'
        count -= 1


if __name__ == '__main__':
    logger.info('Running coin_info.py from module exchange.bybit_api')
    print(get_instrument_info('linear', 'BTCUSDT'))
