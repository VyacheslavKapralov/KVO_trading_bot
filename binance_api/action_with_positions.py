from loguru import logger

from binance_api.get_exchange_client_info import Client
from binance_api.trading import Position


@logger.catch()
def action_choice(symbol: str, exchange_type: str, signal: str | tuple, percentage_deposit: float) -> \
        tuple[bool, tuple | dict | str]:
    if isinstance(signal, str):
        return action_choice_ema(symbol, exchange_type, signal, percentage_deposit)
    if isinstance(signal, tuple):
        return action_choice_fibo(symbol, exchange_type, signal, percentage_deposit)


@logger.catch()
def action_choice_ema(symbol: str, exchange_type: str, signal: str, percentage_deposit: float) -> \
        tuple[bool, dict | str]:
    client = Client(symbol, exchange_type)
    existing_positions = client.get_positions()
    if isinstance(existing_positions, str):
        logger.info(f"Не удалось получить информацию по открытым позициям на бирже: {existing_positions}")
        return False, f"Не удалось получить информацию по открытым позициям на бирже: {existing_positions}"
    new_position = Position(exchange_type, symbol)
    if not existing_positions and signal == "SHORT" or signal == "LONG":
        open_pos = new_position.open_position(data=signal, percentage_deposit=percentage_deposit)
        if isinstance(open_pos, dict):
            logger.info(f"Открытие позиции: {open_pos}")
            return True, open_pos
        else:
            logger.info(f"Не удалось открыть позицию: {open_pos}")
            return False, open_pos
    elif existing_positions and signal == "CLOSE_LONG" or signal == "CLOSE_SHORT":
        side = signal.split('_')[-1]
        for position in existing_positions:
            if position.get('positionSide') == side:
                close_pos = new_position.close_position(position_side=side,
                                                        quantity=abs(float(position.get('positionAmt'))))
                if isinstance(close_pos, str):
                    logger.info(f"Не удалось закрыть позицию: {close_pos}")
                    return False, close_pos
                else:
                    logger.info(f"Закрытие предыдущей позиции: {close_pos}")
                    return True, close_pos
    return False, f"Нет позиций на инструменте {symbol}"


@logger.catch()
def action_choice_fibo(symbol: str, exchange_type: str, signal: tuple, percentage_deposit: float) -> \
        tuple[bool, tuple | str]:
    new_position = Position(exchange_type, symbol)
    open_pos = new_position.open_position(data=signal, percentage_deposit=percentage_deposit)
    if isinstance(open_pos, dict):
        logger.info(f"Размещен ордер: {open_pos}")
        return True, open_pos
    else:
        logger.info(f"Не удалось разместить ордер: {open_pos}")
        return False, open_pos


if __name__ == '__main__':
    logger.info('Running action_with_positions.py from module binance_api')
