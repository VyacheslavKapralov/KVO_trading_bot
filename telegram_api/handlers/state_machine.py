from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger


class StrategyState(StatesGroup):
    strategy = State()
    exchange = State()
    exchange_type = State()
    coin_name = State()
    time_frame = State()
    percentage_deposit = State()


class EmaStrategyState(StatesGroup):
    stop_line = State()
    ema = State()
    ma = State()


class GridState(StatesGroup):
    exchange = State()
    exchange_type = State()
    coin_name = State()
    percentage_deposit = State()
    upper_price = State()
    lower_price = State()
    mesh_threads = State()
    starting_price = State()


if __name__ == '__main__':
    logger.info('Running state_machine.py from module telegram_api/handlers')
