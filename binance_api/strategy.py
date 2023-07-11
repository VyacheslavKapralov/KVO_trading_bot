from loguru import logger

from binance_api.actions_with_positions.close_position import close_position
from binance_api.actions_with_positions.open_position import open_position


@logger.catch()
def action_choice(coin: str, exchange_type: str, position_side: str, percentage_deposit: float, position: tuple):
    if not position:
        result = open_position(coin, exchange_type, position_side, percentage_deposit)
        return True, result

    elif position[0].get('positionSide') != position_side:
        close_position(coin, exchange_type, position_side=position[0].get('positionSide'),
                       quantity=abs(float(position[0].get('positionAmt'))))
        result = open_position(coin, exchange_type, position_side, percentage_deposit)
        return True, result

    else:
        return False, position[0]


if __name__ == '__main__':
    logger.info('Running strategy.py from module binance_api')
