from loguru import logger
from binance.error import ClientError
from binance.spot import Spot
from binance.um_futures import UMFutures

from settings import BinanceSettings


@logger.catch()
def get_balance_futures() -> dict | str:
    try:
        binance_set = BinanceSettings()
        connect_um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                              secret=binance_set.secret_key.get_secret_value())
        return connect_um_futures_client.balance(recvWindow=6000)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_balance_spot() -> dict | str:
    try:
        binance_set = BinanceSettings()
        connect_spot_client = Spot(api_key=binance_set.api_key.get_secret_value(),
                                   api_secret=binance_set.secret_key.get_secret_value())
        return connect_spot_client.balance(recvWindow=6000)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


if __name__ == '__main__':
    logger.info('Running get_balance.py from module binance_api/trade')
