from typing import Generator

from loguru import logger
from binance.error import ClientError
from binance.spot import Spot
from binance.um_futures import UMFutures
from settings import BinanceSettings


@logger.catch()
def get_positions_futures() -> Generator | str:
    binance_set = BinanceSettings()
    connect_um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                          secret=binance_set.secret_key.get_secret_value())
    try:
        positions = connect_um_futures_client.account(recvWindow=10000)['positions']
        return (position for position in positions if float(position['positionAmt']) != 0)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def all_positions(coin: str, exchange_type: str) -> Generator | str:
    if exchange_type == "FUTURES":
        positions = get_positions_futures()
        if isinstance(positions, str):
            logger.info(f"Не удалось получить информацию по открытым позициям на инструменте {coin}: {positions}")
            return positions
        elif isinstance(positions, Generator):
            return (val for val in positions if val.get('symbol') == coin)
    else:
        return ""


if __name__ == '__main__':
    logger.info('Running get_positions.py from module binance_api/client_information')
