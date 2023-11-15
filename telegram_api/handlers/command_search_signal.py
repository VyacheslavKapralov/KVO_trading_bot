import asyncio
import datetime

from loguru import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from database.database import db_write, create_database
from exchanges.trading.action_with_positions import action_choice
from exchanges.working_with_data.time_frames_editing import get_timeout_response, get_waiting_time
from strategies.signal_ema import output_signals_ema
from telegram_api.handlers.command_arrange_grid import command_chancel
from telegram_api.handlers.decorators import check_int
from telegram_api.handlers.keyboards import menu_exchange, menu_exchange_type, menu_ticker, menu_time_frame, \
    menu_percentage, menu_chancel, menu_strategy
from telegram_api.handlers.state_machine import EmaStrategyState, StrategyState

INTERRUPT = False
IGNORE_MESSAGE = False


@logger.catch()
def ignore_messages(func):
    async def wrapper(message: types.Message, state: FSMContext):
        if not IGNORE_MESSAGE:
            return await func(message, state)

    return wrapper


@logger.catch()
async def command_search_signal(message: types.Message):
    global INTERRUPT, IGNORE_MESSAGE
    INTERRUPT = False
    IGNORE_MESSAGE = False
    await StrategyState.strategy.set()
    await message.answer('Выберите стратегию', reply_markup=menu_strategy())


@logger.catch()
async def strategy(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['strategy'] = callback.data
    await StrategyState.next()
    await callback.message.answer('На какой бирже искать сигналы?', reply_markup=menu_exchange())


@logger.catch()
async def change_exchange(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['exchange'] = callback.data.upper()
    await StrategyState.next()
    await callback.message.answer('На какой секции биржи искать сигналы?', reply_markup=menu_exchange_type())


@logger.catch()
async def change_exchange_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['exchange_type'] = callback.data.upper()
    await StrategyState.next()
    await callback.message.answer('Введите тикер инструмента', reply_markup=menu_ticker())


@logger.catch()
async def change_coin_name(callback: types.CallbackQuery, state: FSMContext):
    create_database(callback.data)
    async with state.proxy() as data:
        data['coin_name'] = callback.data
    await StrategyState.next()
    await callback.message.answer('Введите тайм-фрейм данных', reply_markup=menu_time_frame())


@logger.catch()
async def change_time_frame(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['time_frame'] = callback.data
    await StrategyState.next()
    await callback.message.answer('Какой процент от свободного депозита использовать?', reply_markup=menu_percentage())


@logger.catch()
async def change_percentage_deposit(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['percentage_deposit'] = callback.data
    await StrategyState.next()
    if data['strategy'] == 'EMA':
        await EmaStrategyState.stop_line.set()
        await callback.message.answer('Введите период стоп линии основанной на экспоненциальной скользящей средней',
                                      reply_markup=menu_chancel())
    else:
        await callback.message.answer('В разработке...')
        await command_chancel(callback.message, state)


@logger.catch()
@check_int
async def get_ema_stop_period(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stop_line'] = int(message.text)
    await EmaStrategyState.next()
    await message.answer('Введите период быстрой экспоненциальной скользящей средней', reply_markup=menu_chancel())


@logger.catch()
@check_int
async def get_ema_period(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ema'] = int(message.text)
    await EmaStrategyState.next()
    await message.answer('Введите период медленной простой скользящей средней', reply_markup=menu_chancel())


@logger.catch()
@ignore_messages
@check_int
async def get_ma_period(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ma'] = int(message.text)
    global IGNORE_MESSAGE
    IGNORE_MESSAGE = True
    await search_signal(message, state)


@logger.catch()
async def search_signal(message, state):
    async with state.proxy() as data:
        await message.answer(f"Начинаю поиск сигналов на бирже {data['exchange']}\n"
                             f"По стратегии {data['strategy']}\n"
                             f"Параметры поиска:\n"
                             f"Секция биржи: {data['exchange_type']}\n"
                             f"Тикер инструмента: {data['coin_name']}\n"
                             f"Тайм-фрейм: {data['time_frame']}\n"
                             f"Используемый депозит: {data['percentage_deposit']}% от общей суммы\n",
                             reply_markup=menu_chancel())

    timeout_seconds = get_timeout_response(data['time_frame'])
    logger.info(f"Старт поиска сигнала по стратегии {data['strategy']}. Период: {timeout_seconds} сек")
    current_position_last = {'position': None}
    while not INTERRUPT:
        now_time = datetime.datetime.now()
        waiting_time_seconds = get_waiting_time(now_time, data['time_frame'])
        await asyncio.sleep(waiting_time_seconds)
        flag = False
        signal = ''

        if data['strategy'] == 'EMA':
            await message.answer(f"Stop_EMA: {data['stop_line']}\n"
                                 f"EMA: {data['ema']}\n"
                                 f"MA: {data['ma']}",
                                 reply_markup=menu_chancel())
            flag, signal = output_signals_ema(exchange=data['exchange'], exchange_type=data['exchange_type'],
                                              symbol=data['coin_name'], time_frame=data['time_frame'],
                                              period_stop=data['stop_line'], period_fast=data['ema'],
                                              period_slow=data['ma'], current_position_last=current_position_last)

        if flag:
            await message.answer(f"Получен сигнал '{signal}' на инструменте {data['coin_name']},\n"
                                 f"По стратегии: {data['strategy']}\n"
                                 f"На бирже: {data['exchange']},\n")
            success, order = action_choice(exchange=data['exchange'],
                                           strategy=data['strategy'],
                                           symbol=data['coin_name'],
                                           exchange_type=data['exchange_type'],
                                           signal=signal,
                                           percentage_deposit=float(data['percentage_deposit']),
                                           )
            logger.info(f"Ордер: {order}")
            if success:
                await message.answer(f"Размещен лимитный ордер:\n"
                                     f"{order}")
                db_write(
                    date_time=now_time.strftime("%Y-%m-%d %H:%M:%S"),
                    user_name=message.from_user.username,
                    exchange=data['exchange'],
                    exchange_type=data['exchange_type'],
                    strategy=data['strategy'],
                    ticker=data['coin_name'],
                    period=data['time_frame'],
                    signal=signal,
                    position=f"Price: {order.get('price')}; quantity: {order.get('origQty')}; "
                             f"type: {order.get('type')}; stop_price: {order.get('stopPrice')}"
                )
            else:
                await message.answer(order)
        elif isinstance(signal, str):
            await message.answer(signal)
    await command_chancel(message, state)
    logger.info("Поиск сигналов остановлен.")


def register_handlers_commands_search_signal(dp: Dispatcher):
    dp.register_message_handler(command_search_signal, commands=['search'])
    dp.register_callback_query_handler(strategy, state=StrategyState.strategy)
    dp.register_callback_query_handler(change_exchange, state=StrategyState.exchange)
    dp.register_callback_query_handler(change_exchange_type, state=StrategyState.exchange_type)
    dp.register_callback_query_handler(change_coin_name, state=StrategyState.coin_name)
    dp.register_callback_query_handler(change_time_frame, state=StrategyState.time_frame)
    dp.register_callback_query_handler(change_percentage_deposit, state=StrategyState.percentage_deposit)
    dp.register_message_handler(get_ema_stop_period, state=EmaStrategyState.stop_line)
    dp.register_message_handler(get_ema_period, state=EmaStrategyState.ema)
    dp.register_message_handler(get_ma_period, state=EmaStrategyState.ma)


if __name__ == '__main__':
    logger.info('Running ema_command_search.py from module telegram_api/handlers')
