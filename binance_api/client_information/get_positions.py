from typing import Generator
from loguru import logger
from binance.error import ClientError
from binance_api.connect_binance import connect_um_futures_client


@logger.catch()
def get_positions_coin_um_futures(coin: str) -> Generator | str:
    try:
        positions = connect_um_futures_client().account(recvWindow=10000)['positions']
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message
    all_positions = (position for position in positions if float(position['positionAmt']) != 0)
    return (position for position in all_positions if position.get('symbol') == coin)


@logger.catch()
def get_positions(coin: str, exchange_type: str) -> Generator | str:
    if exchange_type == "FUTURES":
        return get_positions_coin_um_futures(coin)
    else:
        return ""


if __name__ == '__main__':
    logger.info('Running get_positions.py from module binance_api/client_information')
