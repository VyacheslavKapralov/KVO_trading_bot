from typing import Any, Generator

from loguru import logger

from binance_api.actions_with_positions.close_position import close_position
from binance_api.client_information.get_positions import get_positions_futures
from binance_api.actions_with_positions.open_position import open_position


@logger.catch()
def action_choice(coin: str, exchange_type: str, position_side: str, percentage_deposit: float):
    positions = tuple(all_positions(coin, exchange_type))

    if not positions:
        result = open_position(coin, exchange_type, position_side, percentage_deposit)
        return True, result

    if len(positions) == 1:
        for elem in positions:
            if elem.get('positionSide') != position_side:
                close_position(coin, exchange_type, position_side=elem.get('positionSide'),
                               quantity=abs(float(elem.get('positionAmt'))))
                result = open_position(coin, exchange_type, position_side, percentage_deposit)
                return True, result

            else:
                return False, elem

    else:
        return False, positions


@logger.catch()
def all_positions(coin: str, exchange_type: str) -> Generator[Any, Any, None]:
    if exchange_type == "FUTURES":
        positions = get_positions_futures()
    else:
        positions = None

    return (val for val in positions if val.get('symbol') == coin)


if __name__ == '__main__':
    logger.info('Running strategy.py from module binance_api')
