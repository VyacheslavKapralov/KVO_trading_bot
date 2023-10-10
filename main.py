from aiogram.utils import executor
from loguru import logger

from logs.start_log import log_telegram_bot
from telegram_api.connect_telegrambot import dp
from telegram_api.handlers import commands


async def on_startup(_):
    log_telegram_bot()
    logger.info('Start KVO_EMA_Binance_bot')


commands.register_handlers_commands(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
