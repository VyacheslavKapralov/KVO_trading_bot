from aiogram.dispatcher.filters.state import StatesGroup, State


class CoinInfoStates(StatesGroup):
    exchange_type = State()
    coin_name = State()
    time_frame = State()
    ema = State()
    ma = State()


if __name__ == '__main__':
    pass
