from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup
from loguru import logger


@logger.catch()
def main_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/search')).add(KeyboardButton('/help'))\
        .add(KeyboardButton('/history'))


@logger.catch()
def search_menu_exchange():
    return InlineKeyboardMarkup(row_width=2).row(
        InlineKeyboardButton(text='FUTURES', callback_data='FUTURES'),
        InlineKeyboardButton(text='SPOT', callback_data='SPOT')
    )


@logger.catch()
def search_menu_ticker():
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
        InlineKeyboardButton(text='MKRUSDT', callback_data='MKRUSDT')
    )


@logger.catch()
def search_menu_time_frame():
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
        # InlineKeyboardButton(text='1 month', callback_data='1M')
    )


if __name__ == '__main__':
    logger.info('Running keyboards.py from module telegram_api/handlers')
