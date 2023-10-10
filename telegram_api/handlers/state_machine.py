from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger


class StrategyState(StatesGroup):
    strategy = State()
    strategy_typ = State()


class EmaStrategyState(StatesGroup):
    start = State()
    exchange = State()
    exchange_type = State()
    coin_name = State()
    time_frame = State()
    percentage_deposit = State()
    stop_line = State()
    ema = State()
    ma = State()


class FiboStrategyState(StatesGroup):
    start = State()
    exchange = State()
    exchange_type = State()
    coin_name = State()
    time_frame = State()
    percentage_deposit = State()


if __name__ == '__main__':
    logger.info('Running state_machine.py from module telegram_api/handlers')
