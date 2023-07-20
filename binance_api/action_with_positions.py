from loguru import logger
from binance_api.add_positions.close_position import close_position
from binance_api.add_positions.open_position import open_position
from binance_api.client_information.get_positions import get_positions


@logger.catch()
def action_choice(coin: str, exchange_type: str, signal: str, percentage_deposit: float) -> tuple[bool, dict | str]:
    existing_positions = get_positions(coin, exchange_type)
    if isinstance(existing_positions, str):
        logger.info(f"Не удалось получить информацию по открытым позициям на бирже: {existing_positions}")
        return False, f"Не удалось получить информацию по открытым позициям на бирже: {existing_positions}"
    if not existing_positions and signal == "SHORT" or signal == "LONG":
        open_pos = open_position(coin, exchange_type, signal, percentage_deposit)
        if isinstance(open_pos, dict):
            logger.info(f"Открытие позиции: {open_pos}")
            return True, open_pos
        else:
            logger.info(f"Не удалось открыть позицию: {open_pos}")
            return False, open_pos
    elif signal == "CLOSE_LONG" or signal == "CLOSE_SHORT" and len(existing_positions) > 0:
        side = signal.split('_')[-1]
        for position in existing_positions:
            if position.get('positionSide') == side:
                close_pos = close_position(coin, exchange_type, position_side=side,
                                           quantity=abs(float(position.get('positionAmt'))))
                if isinstance(close_pos, str):
                    logger.info(f"Не удалось закрыть позицию: {close_pos}")
                    return False, close_pos
                else:
                    logger.info(f"Закрытие предыдущей позиции: {close_pos}")
                    return True, close_pos
    logger.info(f"Нет позиций на инструменте {coin}")
    return False, f"Нет позиций на инструменте {coin}"


if __name__ == '__main__':
    logger.info('Running action_with_positions.py from module binance_api')

