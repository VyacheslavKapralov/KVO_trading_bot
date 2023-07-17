from typing import Generator

from loguru import logger
from binance.error import ClientError
from binance.spot import Spot
from binance.um_futures import UMFutures
from settings import BinanceSettings


@logger.catch()
def get_positions_futures(coin: str) -> Generator | str:
    binance_set = BinanceSettings()
    connect_um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                          secret=binance_set.secret_key.get_secret_value())
    try:
        positions = connect_um_futures_client.account(recvWindow=10000)['positions']
        if isinstance(positions, str):
            logger.info(f"Не удалось получить информацию по открытым позициям на бирже: {positions}")
            return f"Не удалось получить информацию по открытым позициям на бирже: {positions}"
        all_positions = (position for position in positions if float(position['positionAmt']) != 0)
        return (position for position in all_positions if position.get('symbol') == coin)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_positions_coin(coin: str, exchange_type: str) -> Generator | str:
    if exchange_type == "FUTURES":
        return get_positions_futures(coin)
    else:
        return ""


if __name__ == '__main__':
    logger.info('Running get_positions.py from module binance_api/client_information')
