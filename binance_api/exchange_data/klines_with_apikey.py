from loguru import logger
from binance.error import ClientError
from binance.um_futures import UMFutures

from settings import BinanceSettings


@logger.catch()
def historical_klines_futures(symbol, timeframe):
    try:
        binance_set = BinanceSettings()

        um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                      secret=binance_set.secret_key.get_secret_value())
        return um_futures_client.klines(symbol, timeframe)
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
        binance_set = BinanceSettings()

        um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                      secret=binance_set.secret_key.get_secret_value())
        return um_futures_client.continuous_klines(symbol, "PERPETUAL", period)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


if __name__ == '__main__':
    logger.info('Running klines_with_apikey.py from module binance_api')
