from aiogram.types import BotCommand, BotCommandScope
from aiogram.utils import executor
from loguru import logger

from logs.start_log import log_telegram_bot
from telegram_api.connect_telegrambot import bot, dp
from telegram_api.handlers import arrange_grid, commands, search_signal, search_volatile_coins
from telegram_api.handlers.commands import commands_dict


@logger.catch()
async def set_bot_commands():
    scope = BotCommandScope()
    scope.type = "all_private_chats"
    await bot.delete_my_commands(scope)
    bot_commands = [BotCommand(command=cmd, description=desc) for cmd, desc in commands_dict.items()]
    await bot.set_my_commands(bot_commands)


@logger.catch()
async def main(_):
    await set_bot_commands()
    log_telegram_bot()
    commands.register_handlers_commands(dp)
    search_signal.register_handlers_commands_search_signal(dp)
    arrange_grid.register_handlers_commands_arrange_grid(dp)
    search_volatile_coins.register_handlers_commands_volatile(dp)
    logger.info('Start KVO_trading_bot')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=main)


