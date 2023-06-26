from aiogram import Bot, Dispatcher
from loguru import logger
from settings import BotSettings
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware


@logger.catch()
def connect():
    """
    connect() - эта функция используется для установления соединения с Telegram-ботом.
    Аргументы: Нет.
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
    logger.info('Start connect_telegrambot.py')
