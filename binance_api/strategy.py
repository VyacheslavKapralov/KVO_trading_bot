from loguru import logger

from binance_api.client_information.get_positions import get_positions_futures
from binance_api.actions_with_positions.open_position import open_position


@logger.catch()
def action_choice(coin, exchange_type, position_side, percentage_deposit):
    position = get_positions_coin(coin, exchange_type, position_side)
    if not position:
        result = open_position(coin, exchange_type, position_side, percentage_deposit)
        return True, result
    else:
        return False, position


@logger.catch()
def get_positions_coin(coin, exchange_type, position_side):
    if exchange_type == "FUTURES":
        positions = get_positions_futures()
    else:
        positions = None

    positions_coin = [elem for elem in positions if elem.get('symbol') == coin]

    for elem in positions_coin:
        if elem.get('positionSide') != position_side:
            return None
        else:
            return elem


if __name__ == '__main__':
    logger.info('Running strategy.py from module binance_api')
