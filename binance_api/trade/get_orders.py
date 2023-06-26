from loguru import logger
from binance.error import ClientError
from binance.spot import Spot
from binance.um_futures import UMFutures
from settings import BinanceSettings

binance_set = BinanceSettings()


@logger.catch()
def get_all_orders_futures(symbol: str):
    try:
        connect_um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                              secret=binance_set.secret_key.get_secret_value())
        return connect_um_futures_client.get_all_orders(symbol=symbol, recvWindow=6000)

    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_orders_futures(symbol: str):
    try:
        connect_um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                              secret=binance_set.secret_key.get_secret_value())
        return connect_um_futures_client.get_orders(symbol=symbol, recvWindow=6000)

    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_all_orders_spot(symbol: str):
    try:
        connect_spot_client = Spot(api_key=binance_set.api_key.get_secret_value(),
                                   api_secret=binance_set.secret_key.get_secret_value())
        return connect_spot_client.get_orders(symbol=symbol, recvWindow=6000)

    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


if __name__ == '__main__':
    logger.info('Running get_orders.py from module binance_api/trade')
