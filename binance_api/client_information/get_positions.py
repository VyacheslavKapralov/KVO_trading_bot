from loguru import logger
from binance.error import ClientError
from binance.spot import Spot
from binance.um_futures import UMFutures
from settings import BinanceSettings


@logger.catch()
def get_positions_futures():
    binance_set = BinanceSettings()
    connect_um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                          secret=binance_set.secret_key.get_secret_value())
    try:
        positions = connect_um_futures_client.account(recvWindow=6000)['positions']
        not_null_positions = (position for position in positions if
                              float(position['askNotional']) > 0 or float(position['bidNotional']) > 0)

        return not_null_positions

    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


if __name__ == '__main__':
    logger.info('Running get_positions.py from module binance_api/client_information')
