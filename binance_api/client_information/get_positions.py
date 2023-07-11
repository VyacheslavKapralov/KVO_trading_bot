from typing import Any, Generator

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
        not_null_positions = (position for position in positions if float(position['positionAmt']) != 0)
        return not_null_positions

    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def all_positions(coin: str, exchange_type: str) -> Generator[Any, Any, None]:
    if exchange_type == "FUTURES":
        positions = get_positions_futures()
    else:
        positions = None

    return (val for val in positions if val.get('symbol') == coin)


if __name__ == '__main__':
    logger.info('Running get_positions.py from module binance_api/client_information')