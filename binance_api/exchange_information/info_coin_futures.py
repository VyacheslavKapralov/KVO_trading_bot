from loguru import logger
from binance.error import ClientError
from binance.um_futures import UMFutures
from binance_api.connect_binance import connect_um_futures_client


um_futures_client = connect_um_futures_client()


@logger.catch()
def book_ticker_futures(symbol):
    try:
        return um_futures_client.book_ticker(symbol)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def continuous_klines_futures(symbol: str, period: str):
    try:
        return um_futures_client.continuous_klines(symbol, "PERPETUAL", period)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def exchange_info_futures():
    try:
        return um_futures_client.exchange_info()
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def commission_rate_futures(symbol):
    try:
        return um_futures_client.commission_rate(symbol=symbol, recvWindow=6000)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_orders_futures(symbol):
    try:
        return um_futures_client.get_all_orders(symbol=symbol, recvWindow=6000)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def historical_klines_futures(symbol, timeframe):
    try:
        _um_futures_client = UMFutures()
        return _um_futures_client.klines(symbol, timeframe)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


if __name__ == '__main__':
    logger.info('Running info_coin_futures.py'
                ' from module binance_api')
