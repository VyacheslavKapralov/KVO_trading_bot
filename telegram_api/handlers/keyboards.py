from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup
from loguru import logger


@logger.catch()
def main_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
        .add(KeyboardButton('/search'))\
        .add(KeyboardButton('/help'))\
        .add(KeyboardButton('/history'))


@logger.catch()
def menu_strategy():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Intersection EMA and MA', callback_data='EMA'),
        InlineKeyboardButton(text='Correction Fibonacci', callback_data='FIBO'),
        InlineKeyboardButton(text='Smart Money Management', callback_data='SMM'),
    )


@logger.catch()
def menu_chancel():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/chancel'))


@logger.catch()
def menu_exchange():
    return InlineKeyboardMarkup(row_width=2).row(
        InlineKeyboardButton(text='BINANCE', callback_data='BINANCE'),
        InlineKeyboardButton(text='BYBIT', callback_data='BYBIT'),
    )


@logger.catch()
def menu_exchange_type():
    return InlineKeyboardMarkup(row_width=2).row(
        InlineKeyboardButton(text='FUTURES', callback_data='FUTURES'),
        InlineKeyboardButton(text='SPOT', callback_data='SPOT'),
    )


@logger.catch()
def menu_ticker():
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton(text='BTCUSDT', callback_data='BTCUSDT'),
        InlineKeyboardButton(text='ETHUSDT', callback_data='ETHUSDT'),
        InlineKeyboardButton(text='BCHUSDT', callback_data='BCHUSDT'),
        InlineKeyboardButton(text='LTCUSDT', callback_data='LTCUSDT'),
        InlineKeyboardButton(text='YFIUSDT', callback_data='YFIUSDT'),
        InlineKeyboardButton(text='BNBUSDT', callback_data='BNBUSDT'),
        InlineKeyboardButton(text='SOLUSDT', callback_data='SOLUSDT'),
        InlineKeyboardButton(text='ATOMUSDT', callback_data='ATOMUSDT'),
        InlineKeyboardButton(text='LINKUSDT', callback_data='LINKUSDT'),
        InlineKeyboardButton(text='MKRUSDT', callback_data='MKRUSDT'),
    )


@logger.catch()
def menu_time_frame():
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton(text='1 minute', callback_data='1m'),
        InlineKeyboardButton(text='5 minutes', callback_data='5m'),
        InlineKeyboardButton(text='15 minutes', callback_data='15m'),
        InlineKeyboardButton(text='30 minutes', callback_data='30m'),
        InlineKeyboardButton(text='1 hour', callback_data='1h'),
        InlineKeyboardButton(text='2 hours', callback_data='2h'),
        InlineKeyboardButton(text='4 hours', callback_data='4h'),
        InlineKeyboardButton(text='6 hours', callback_data='6h'),
        InlineKeyboardButton(text='8 hours', callback_data='8h'),
        InlineKeyboardButton(text='12 hours', callback_data='12h'),
        InlineKeyboardButton(text='1 day', callback_data='1d'),
        InlineKeyboardButton(text='1 week', callback_data='1w'),
        # InlineKeyboardButton(text='1 month', callback_data='1M'),
    )


@logger.catch()
def menu_percentage():
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton(text='2', callback_data='2'),
        InlineKeyboardButton(text='3', callback_data='3'),
        InlineKeyboardButton(text='5', callback_data='5'),
        InlineKeyboardButton(text='10', callback_data='10'),
        InlineKeyboardButton(text='20', callback_data='20'),
        InlineKeyboardButton(text='30', callback_data='30'),
        InlineKeyboardButton(text='50', callback_data='50'),
        InlineKeyboardButton(text='75', callback_data='75'),
        InlineKeyboardButton(text='100', callback_data='100'),
    )


if __name__ == '__main__':
    logger.info('Running keyboards.py from module telegram_api/handlers')
