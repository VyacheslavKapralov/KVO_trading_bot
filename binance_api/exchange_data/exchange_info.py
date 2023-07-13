from loguru import logger
from binance.error import ClientError
from binance.um_futures import UMFutures

from settings import BinanceSettings


@logger.catch()
def exchange_info_futures() -> dict | str:
    try:
        binance_set = BinanceSettings()
        connect_um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                              secret=binance_set.secret_key.get_secret_value())
        return connect_um_futures_client.exchange_info()
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


if __name__ == '__main__':
    logger.info('Running exchange_info.py from module binance_api/exchange_data')
