from binance.spot import Spot
from binance.cm_futures import CMFutures
from binance.um_futures import UMFutures
from binance.error import ClientError
from settings import BinanceSettings
from loguru import logger


@logger.catch()
def connect_cm_futures_client():
    binance_set = BinanceSettings()
    try:
        return CMFutures(key=binance_set.api_key.get_secret_value(), secret=binance_set.secret_key.get_secret_value())
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


@logger.catch()
def connect_um_futures_client():
    binance_set = BinanceSettings()
    try:
        return UMFutures(key=binance_set.api_key.get_secret_value(), secret=binance_set.secret_key.get_secret_value())
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


@logger.catch()
def connect_spot_client():
    binance_set = BinanceSettings()
    try:
        return Spot(api_key=binance_set.api_key.get_secret_value(),
                    api_secret=binance_set.secret_key.get_secret_value())
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


if __name__ == '__main__':
    logger.info('Running connect_binance.py from module binance_api')
