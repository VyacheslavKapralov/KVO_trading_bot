from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger


class CoinInfoStates(StatesGroup):
    exchange_type = State()
    coin_name = State()
    time_frame = State()
    percentage_deposit = State()
    trend_line = State()
    ema = State()
    ma = State()


if __name__ == '__main__':
    logger.info('Running state_machine.py from module telegram_api/handlers')
