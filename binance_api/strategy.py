from loguru import logger

from binance_api.actions_with_positions.close_position import close_position
from binance_api.actions_with_positions.open_position import open_position


@logger.catch()
def action_choice(coin: str, exchange_type: str, position_side: str, percentage_deposit: float,
                  position: tuple) -> tuple[bool, dict | str]:
    if not position:
        open_pos = open_position(coin, exchange_type, position_side, percentage_deposit)
        if isinstance(open_pos, dict):
            logger.info(f"Открытие позиции: {open_pos}")
            return True, open_pos
        else:
            logger.info(open_pos)
            return False, open_pos
    elif position[0].get('positionSide') != position_side:
        close_pos = close_position(coin, exchange_type, position_side=position[0].get('positionSide'),
                                   quantity=abs(float(position[0].get('positionAmt'))))
        if isinstance(close_pos, str):
            logger.info(f"Не удалось закрыть позицию: {close_pos}")
            return False, close_pos
        open_pos = open_position(coin, exchange_type, position_side, percentage_deposit)
        if isinstance(open_pos, str):
            logger.info(f"Не удалось открыть позицию: {open_pos}")
            return False, open_pos
        else:
            logger.info(f"Закрытие предыдущей позиции: {close_pos}")
            logger.info(f"Открытие позиции: {open_pos}")
            return True, open_pos
    else:
        return False, f"На данном активе уже есть попутная позиция:\n{position[0]}"


if __name__ == '__main__':
    logger.info('Running strategy.py from module binance_api')
