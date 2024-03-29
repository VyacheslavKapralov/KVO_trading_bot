from aiogram import Bot, Dispatcher
from loguru import logger
from settings import BotSettings
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware


@logger.catch()
def connect():
    """
    Функция используется для установления соединения с Telegram-ботом.
    Возвращаемое значение: bott, dispatcher - два объекта для работы с ботом и диспетчером.
    """

    telebot = BotSettings()
    bott = Bot(token=telebot.telebot_api.get_secret_value())
    storage = MemoryStorage()
    dispatcher = Dispatcher(bott, storage=storage)
    dispatcher.middleware.setup(LoggingMiddleware())
    return bott, dispatcher


bot, dp = connect()


if __name__ == '__main__':
    logger.info('Running connect_telegrambot.py from module telegram_api')
