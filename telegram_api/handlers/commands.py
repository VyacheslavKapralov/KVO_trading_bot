from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loguru import logger
from database.database import db_read
from telegram_api.handlers.ema_command_search import ema_command_search_signal, ema_command_chancel, ema_change_exchange, ema_change_exchange_type, \
    ema_change_coin_name, ema_change_time_frame, ema_change_percentage_deposit, ema_get_stop_period, get_ema_period, get_ma_period
from telegram_api.handlers.fibo_command_search import fibo_command_chancel, fibo_command_search_signal, \
    fibo_change_exchange, fibo_change_exchange_type, fibo_change_coin_name, fibo_change_time_frame, \
    fibo_change_percentage_deposit
from telegram_api.handlers.keyboards import main_menu, menu_strategy
from telegram_api.handlers.state_machine import StrategyState, EmaStrategyState, FiboStrategyState


@logger.catch()
async def command_start(message: types.Message):
    await message.answer(f"Добро пожаловать, {message.from_user.first_name}. "
                         f"Я бот, умеющий взаимодействовать с биржей Binance.\n"
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
async def command_search(message: types.Message):
    await StrategyState.strategy.set()
    await message.answer('Выберите стратегию', reply_markup=menu_strategy())


@logger.catch()
async def strategy(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    if callback.data == 'EMA':
        await EmaStrategyState.start.set()
        await ema_command_search_signal(callback)
    elif callback.data == 'FIBO':
        await FiboStrategyState.start.set()
        await fibo_command_search_signal(callback)


@logger.catch()
def register_handlers_commands(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'старт', 'info', 'инфо', 'help', 'помощь'])
    # dp.register_message_handler(command_history, commands=['history', 'история'])
    dp.register_message_handler(command_search, commands=['search'])
    dp.register_callback_query_handler(strategy, state=StrategyState.strategy)
    dp.register_message_handler(ema_command_chancel, commands=['сброс', 'прервать', 'chancel'], state='*')
    dp.register_message_handler(ema_command_chancel, Text(equals=['сброс', 'прервать', 'chancel'], ignore_case=True),
                                state='*')
    dp.register_callback_query_handler(ema_command_search_signal, state=EmaStrategyState.start)
    dp.register_callback_query_handler(ema_change_exchange, state=EmaStrategyState.exchange)
    dp.register_callback_query_handler(ema_change_exchange_type, state=EmaStrategyState.exchange_type)
    dp.register_callback_query_handler(ema_change_coin_name, state=EmaStrategyState.coin_name)
    dp.register_callback_query_handler(ema_change_time_frame, state=EmaStrategyState.time_frame)
    dp.register_callback_query_handler(ema_change_percentage_deposit, state=EmaStrategyState.percentage_deposit)
    dp.register_message_handler(ema_get_stop_period, state=EmaStrategyState.stop_line)
    dp.register_message_handler(get_ema_period, state=EmaStrategyState.ema)
    dp.register_message_handler(get_ma_period, state=EmaStrategyState.ma)
    dp.register_message_handler(fibo_command_chancel, commands=['сброс', 'прервать', 'chancel'], state='*')
    dp.register_message_handler(fibo_command_chancel, Text(equals=['сброс', 'прервать', 'chancel'], ignore_case=True),
                                state='*')
    dp.register_callback_query_handler(fibo_command_search_signal, state=FiboStrategyState.start)
    dp.register_callback_query_handler(fibo_change_exchange, state=FiboStrategyState.exchange)
    dp.register_callback_query_handler(fibo_change_exchange_type, state=FiboStrategyState.exchange_type)
    dp.register_callback_query_handler(fibo_change_coin_name, state=FiboStrategyState.coin_name)
    dp.register_callback_query_handler(fibo_change_time_frame, state=FiboStrategyState.time_frame)
    dp.register_callback_query_handler(fibo_change_percentage_deposit, state=FiboStrategyState.percentage_deposit)


if __name__ == '__main__':
    logger.info('Running commands.py from module telegram_api/handlers')
