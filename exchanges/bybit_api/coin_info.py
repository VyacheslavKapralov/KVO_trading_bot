from loguru import logger

from exchanges.bybit_api.connect_bybit import connect_bybit
from pybit.exceptions import InvalidRequestError


@logger.catch()
def get_instrument_info_bybit(exchange_type: str, symbol: str):
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
def get_tickers_bybit(exchange_type: str, symbol: str):
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
    return f"Не удалось получить данные от биржи."


@logger.catch()
def get_orderbook_bybit(exchange_type: str, symbol: str):
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
    return f"Не удалось получить данные от биржи."


@logger.catch()
def get_fee_bybit(exchange_type: str, symbol: str):
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
    return f"Не удалось получить данные от биржи."


@logger.catch()
def get_kline_bybit(exchange_type: str, symbol: str, time_frame: int, limit: int = 500):
    count = 3
    while count > 0:
        session = connect_bybit()
        if not isinstance(session, str):
            try:
                return session.get_kline(
                    category=exchange_type,
                    symbol=symbol,
                    interval=time_frame,
                    # limit=limit,
                )
            except InvalidRequestError as error:
                logger.info(f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                            f"error message: {error.message}")
                return f'Error code: {error.status_code} - {error.message}'
        count -= 1
    return f"Не удалось получить данные от биржи."


if __name__ == '__main__':
    logger.info('Running coin_info.py from module exchange.bybit_api')
