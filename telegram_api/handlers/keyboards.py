from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
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
        # InlineKeyboardButton(text='Intersection EMA and MA', callback_data='EMA'),
        # InlineKeyboardButton(text='Correction Fibonacci', callback_data='FIBO'),
        # InlineKeyboardButton(text='Smart Money Management', callback_data='SMM'),
        InlineKeyboardButton(text='Fractals', callback_data='FRACTAL'),
    )


@logger.catch()
def menu_chancel():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        # KeyboardButton('/back'),
        KeyboardButton('/chancel'),
    )


@logger.catch()
def menu_exchange():
    return InlineKeyboardMarkup(row_width=2).row(
        # InlineKeyboardButton(text='BINANCE', callback_data='BINANCE'),
        InlineKeyboardButton(text='BYBIT', callback_data='BYBIT'),
    )


@logger.catch()
def menu_exchange_type():
    return InlineKeyboardMarkup(row_width=2).row(
        InlineKeyboardButton(text='FUTURES', callback_data='FUTURES'),
        # InlineKeyboardButton(text='SPOT', callback_data='SPOT'),
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
    return InlineKeyboardMarkup(row_width=4).add(
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


@logger.catch()
def menu_price_stop():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='В процентах от депозита', callback_data='percent'),
        InlineKeyboardButton(text='В USDT от цены входа', callback_data='usdt'),
        InlineKeyboardButton(text='В ATR равный периоду индикатора', callback_data='atr'),
    )


@logger.catch()
def menu_rollback():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Применить откат в USDT', callback_data='usdt'),
        InlineKeyboardButton(text='Применить откат в ATR', callback_data='atr'),
        InlineKeyboardButton(text='Применить откат в процентах', callback_data='percent'),
        InlineKeyboardButton(text='Не применять откат', callback_data='None'),
    )


@logger.catch()
def menu_ascending():
    return InlineKeyboardMarkup(row_width=2).row(
        InlineKeyboardButton(text='По возрастанию', callback_data='True'),
        InlineKeyboardButton(text='По убыванию', callback_data='False'),
    )


@logger.catch()
def menu_period():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='За минуту', callback_data='1m'),
        InlineKeyboardButton(text='За 5 минут', callback_data='5m'),
        InlineKeyboardButton(text='За 15 минут', callback_data='15m'),
        InlineKeyboardButton(text='За 30 минут', callback_data='30m'),
        InlineKeyboardButton(text='За час', callback_data='1h'),
        InlineKeyboardButton(text='За 2 часа', callback_data='2h'),
        InlineKeyboardButton(text='За 4 часа', callback_data='4h'),
        InlineKeyboardButton(text='За 6 часов', callback_data='6h'),
        InlineKeyboardButton(text='За 8 часов', callback_data='8h'),
        InlineKeyboardButton(text='За 12 часов', callback_data='12h'),
        InlineKeyboardButton(text='За 1 день', callback_data='1d'),
        InlineKeyboardButton(text='За неделю', callback_data='1w'),
        InlineKeyboardButton(text='За месяц', callback_data='1M'),
    )


if __name__ == '__main__':
    logger.info('Running keyboards.py from module telegram_api/handlers')
