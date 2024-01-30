from aiogram.utils import executor
from loguru import logger

from logs.start_log import log_telegram_bot
from telegram_api.connect_telegrambot import bot, dp
from telegram_api.handlers import commands, command_search_signal, command_arrange_grid
from telegram_api.handlers.commands import commands_list


async def on_startup(_):
    log_telegram_bot()
    logger.info('Start KVO_trading_bot')


commands.register_handlers_commands(dp)
command_search_signal.register_handlers_commands_search_signal(dp)
command_arrange_grid.register_handlers_commands_arrange_grid(dp)


if __name__ == '__main__':
    # bot.set_my_commands(commands=commands_list)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

