from loguru import logger

from exchanges.working_with_data.add_dataframe import add_data_frame
from strategies.signal_fractals import fractal_strategy


@logger.catch()
def launch_strategy(strategy_settings: dict) -> tuple[bool, dict | str]:
    match strategy_settings['exchange'], strategy_settings['strategy']:
        case 'BINANCE', 'EMA':
            return action_choice_ema_binance(strategy_settings)
        case 'BINANCE', 'FIBO':
            return action_choice_fibo_binance(strategy_settings)
        case 'BINANCE', 'FRACTAL':
            return
        case 'BYBIT', 'EMA':
            return action_choice_ema_bybit(strategy_settings)
        case 'BYBIT', 'FIBO':
            return action_choice_fibo_bybit(strategy_settings)
        case 'BYBIT', 'FRACTAL':

            return


@logger.catch()
def action_choice_ema_binance(strategy_settings) -> tuple[bool, dict | str]:
    pass
    # client = Client(strategy_settings['exchange'], exchange_type, symbol)
    # existing_positions = client.get_positions()
    # if isinstance(existing_positions, str):
    #     logger.info(f"Не удалось получить информацию по открытым позициям на бирже: {existing_positions}")
    #     return False, f"Не удалось получить информацию по открытым позициям на бирже: {existing_positions}"
    # new_position = Position(exchange, exchange_type, symbol, 'EMA')
    # if not existing_positions and signal == "SHORT" or signal == "LONG":
    #     open_pos = new_position.open_position(data=signal, percentage_deposit=percentage_deposit)
    #     if isinstance(open_pos, str):
    #         logger.info(f"Не удалось открыть позицию: {open_pos}")
    #         return False, open_pos
    #     else:
    #         logger.info(f"Открытие позиции: {open_pos}")
    #         return True, open_pos
    # 
    # elif existing_positions and signal == "CLOSE_LONG" or signal == "CLOSE_SHORT":
    #     side = signal.split('_')[-1]
    #     for position in existing_positions:
    #         if position.get('positionSide') == side:
    #             close_pos = new_position.close_position(position_side=side,
    #                                                     quantity=abs(float(position.get('positionAmt'))))
    #             if isinstance(close_pos, str):
    #                 logger.info(f"Не удалось закрыть позицию: {close_pos}")
    #                 return False, close_pos
    #             else:
    #                 logger.info(f"Закрытие предыдущей позиции: {close_pos}")
    #                 return True, close_pos
    # return False, f"Нет позиций на инструменте {symbol}"


@logger.catch()
def action_choice_fibo_binance(strategy_settings):
    pass
    # new_position = Position(exchange, exchange_type, symbol)
    # open_pos = new_position.open_position(data=signal, percentage_deposit=percentage_deposit)
    # if isinstance(open_pos, str):
    #     logger.info(f"Не удалось разместить ордер: {open_pos}")
    #     return False, open_pos
    # else:
    #     logger.info(f"Размещен ордер: {open_pos}")
    #     return True, open_pos


@logger.catch()
def action_choice_ema_bybit(strategy_settings):
    pass


@logger.catch()
def action_choice_fibo_bybit(strategy_settings):
    pass


if __name__ == '__main__':
    logger.info('Running action_with_positions.py from module binance_api')
