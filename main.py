from aiogram.utils import executor
from loguru import logger

from database.database import create_database
from logs.start_log import log_telegram_bot
from telegram_api.connect_telegrambot import dp
from telegram_api.handlers import other_commands, command_search


async def on_startup(_):
    create_database()
    log_telegram_bot()
    logger.info('Start KVO_EMA_Binance_bot')


other_commands.register_handlers_commands(dp)
command_search.register_handlers_commands_signal(dp)

if __name__ == '__main__':
    logger.info("Запуск main.py")

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
