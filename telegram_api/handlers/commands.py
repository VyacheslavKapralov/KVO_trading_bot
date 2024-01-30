from aiogram import Dispatcher, types
from loguru import logger
from database.database import db_read
from telegram_api.handlers.keyboards import main_menu

commands_list = [
    types.BotCommand(command='start', description='Запустить бота'),
    types.BotCommand(command='info', description='Информация о боте'),
    types.BotCommand(command='help', description='Помощь в работе с ботом'),
    types.BotCommand(command='history', description='Запустить поиск сигналов'),
    # types.BotCommand(command='search', description='Запустить поиск сигналов'),
]


@logger.catch()
async def command_start(message: types.Message):
    await message.answer(f"Добро пожаловать, {message.from_user.first_name}. "
                         f"Я бот, умеющий взаимодействовать с крипто-биржами Binance и Bybit.\n"
                         f"Нажми /search",
                         reply_markup=main_menu()
                         )


@logger.catch()
async def command_history(message: types.Message):
    history = await db_read()
    for elem in history:
        await message.answer(f"Дата: {elem[0]},\n"
                             f"Секция: {elem[3]}\n"
                             f"Тикер: {elem[4]}\n"
                             f"Период: {elem[5]}\n"
                             f"EMA: {elem[6]}\n"
                             f"MA: {elem[7]}\n"
                             f"Сигнал: {elem[8]}")


@logger.catch()
def register_handlers_commands(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'старт', 'info', 'инфо', 'help', 'помощь'])
    # dp.register_message_handler(command_history, commands=['history', 'история'])
    # ToDO: нужно исправить вывод истории: разные стратегии должны выводить разную информацию.


if __name__ == '__main__':
    logger.info('Running commands.py from module telegram_api/handlers')
