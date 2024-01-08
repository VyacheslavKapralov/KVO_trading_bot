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
    menu_percentage, menu_chancel, menu_strategy, menu_price_stop
from telegram_api.handlers.state_machine import EmaStrategyState, StrategyState, FractalStrategyState

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
    async with state.proxy() as strategy_settings:
        strategy_settings['strategy'] = callback.data
    await StrategyState.next()
    await callback.message.answer('На какой бирже искать сигналы?', reply_markup=menu_exchange())


@logger.catch()
async def change_exchange(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['exchange'] = callback.data.upper()
    await StrategyState.next()
    await callback.message.answer('На какой секции биржи искать сигналы?', reply_markup=menu_exchange_type())


@logger.catch()
async def change_exchange_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['exchange_type'] = callback.data.upper()
    await StrategyState.next()
    await callback.message.answer('Введите тикер инструмента', reply_markup=menu_ticker())


@logger.catch()
async def change_coin_name(callback: types.CallbackQuery, state: FSMContext):
    create_database(callback.data)
    async with state.proxy() as strategy_settings:
        strategy_settings['coin_name'] = callback.data
    await StrategyState.next()
    await callback.message.answer('Введите тайм-фрейм данных', reply_markup=menu_time_frame())


@logger.catch()
async def change_time_frame(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['time_frame'] = callback.data
    await StrategyState.next()
    await callback.message.answer('Какой процент от свободного депозита использовать?', reply_markup=menu_percentage())


@logger.catch()
async def change_percentage_deposit(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['percentage_deposit'] = callback.data
    await StrategyState.next()
    if strategy_settings['strategy'] == 'EMA':
        await EmaStrategyState.stop_line.set()
        await callback.message.answer('Введите период стоп линии основанной на экспоненциальной скользящей средней',
                                      reply_markup=menu_chancel())
    elif strategy_settings['strategy'] == 'FRACTAL':
        await FractalStrategyState.period.set()
        await callback.message.answer('Задайте период фракталов')

    else:
        await callback.message.answer('В разработке...')
        await command_chancel(callback.message, state)


@logger.catch()
@check_int
async def get_ema_stop_period(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['stop_line'] = int(message.text)
    await EmaStrategyState.next()
    await message.answer('Введите период быстрой экспоненциальной скользящей средней', reply_markup=menu_chancel())


@logger.catch()
@check_int
async def get_ema_period(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['ema'] = int(message.text)
    await EmaStrategyState.next()
    await message.answer('Введите период медленной простой скользящей средней', reply_markup=menu_chancel())


@logger.catch()
@ignore_messages
@check_int
async def get_ma_period(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['ma'] = int(message.text)
    await search_signal(message, state)


@logger.catch()
@check_int
async def get_period_fractal(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['period'] = int(message.text)
    await FractalStrategyState.next()
    await message.answer('В чем измерять размер stop-loss?', reply_markup=menu_price_stop())


@logger.catch()
async def stop_loss_selection_fractal(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['stop_loss'] = 'atr'
        strategy_settings['stop_loss_selection'] = callback.data
    if callback.data == 'percent' or callback.data == 'usdt':
        await callback.message.answer('Введите размер stop-loss', reply_markup=menu_price_stop())
        return await FractalStrategyState.next()
    await FractalStrategyState.take_profit_selection.set()


@logger.catch()
async def get_stop_loss_fractal(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['stop_loss'] = float(message.text)
    await FractalStrategyState.next()
    await message.answer('В чем измерять размер take-profit?', reply_markup=menu_price_stop())


@logger.catch()
async def take_profit_selection_fractal(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['take_profit_selection'] = callback.data
    if callback.data == 'percent' or callback.data == 'usdt':
        await callback.message.answer('Введите размер take-profit', reply_markup=menu_price_stop())
        return await FractalStrategyState.next()
    await callback.message.answer('Введите множитель (целое число) значения ATR для установки take-profit')
    await FractalStrategyState.multiplicity_atr()


@logger.catch()
@check_int
async def get_multiplicity_atr_fractal(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['take_profit'] = f'multiplicity_atr = {message.text}'
        strategy_settings['multiplicity_atr'] = int(message.text)
    await search_signal(message, state)


@logger.catch()
@ignore_messages
async def get_take_profit_fractal(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['take_profit'] = float(message.text)
    await search_signal(message, state)


@logger.catch()
async def search_signal(message, state):
    global IGNORE_MESSAGE
    IGNORE_MESSAGE = True
    async with state.proxy() as strategy_settings:
        await sending_start_message(strategy_settings, message)

    timeout_seconds = get_timeout_response(strategy_settings['time_frame'])
    logger.info(f"Старт поиска сигнала по стратегии {strategy_settings['strategy']}. Период: {timeout_seconds} сек")
    current_position_last = {'position': None}
    while not INTERRUPT:
        now_time = datetime.datetime.now()
        waiting_time_seconds = get_waiting_time(now_time, strategy_settings['time_frame'])
        await asyncio.sleep(waiting_time_seconds)
        success = None
        signal = ''

        if strategy_settings['strategy'] == 'EMA':
            sending_start_ema_strategy(strategy_settings, message)
            flag, signal = output_signals_ema(
                exchange=strategy_settings['exchange'],
                exchange_type=strategy_settings['exchange_type'],
                symbol=strategy_settings['coin_name'],
                time_frame=strategy_settings['time_frame'],
                period_stop=strategy_settings['stop_line'],
                period_fast=strategy_settings['ema'],
                period_slow=strategy_settings['ma'],
                current_position_last=current_position_last
            )
            if flag:
                await sending_signal_message(strategy_settings, message, signal)
                success, order = action_choice(
                    exchange=strategy_settings['exchange'],
                    strategy=strategy_settings['strategy'],
                    symbol=strategy_settings['coin_name'],
                    exchange_type=strategy_settings['exchange_type'],
                    signal=signal,
                    percentage_deposit=float(strategy_settings['percentage_deposit']),
                )
                logger.info(f"Ордер: {order}")

        elif strategy_settings['strategy'] == 'FRACTAL':
            await sending_start_fractal_strategy(strategy_settings, message)
            # success, order =

        if success:
            await message.answer(f"Размещен лимитный ордер:\n"
                                 f"{order}")
            db_write(
                date_time=now_time.strftime("%Y-%m-%d %H:%M:%S"),
                user_name=message.from_user.username,
                exchange=strategy_settings['exchange'],
                exchange_type=strategy_settings['exchange_type'],
                strategy=strategy_settings['strategy'],
                ticker=strategy_settings['coin_name'],
                period=strategy_settings['time_frame'],
                signal=signal,
                position=f"Price: {order.get('price')}; quantity: {order.get('origQty')}; "
                         f"type: {order.get('type')}; stop_price: {order.get('stopPrice')}"
            )
        else:
            await message.answer(order)
    await command_chancel(message, state)
    logger.info("Поиск сигналов остановлен.")


@logger.catch()
async def sending_start_message(data, message):
    await message.answer(f"Начинаю поиск сигналов на бирже {data['exchange']}\n"
                         f"По стратегии {data['strategy']}\n"
                         f"Параметры поиска:\n"
                         f"Секция биржи: {data['exchange_type']}\n"
                         f"Тикер инструмента: {data['coin_name']}\n"
                         f"Тайм-фрейм: {data['time_frame']}\n"
                         f"Используемый депозит: {data['percentage_deposit']}% от общей суммы\n",
                         reply_markup=menu_chancel())


@logger.catch()
async def sending_signal_message(strategy_settings, message, signal):
    await message.answer(f"Получен сигнал '{strategy_settings}' на инструменте {strategy_settings['coin_name']},\n"
                         f"По стратегии: {strategy_settings['strategy']}\n"
                         f"На бирже: {strategy_settings['exchange']}\n",
                         reply_markup=menu_chancel())


@logger.catch()
async def sending_start_ema_strategy(strategy_settings, message):
    await message.answer(f"Stop_EMA: {strategy_settings['stop_line']}\n"
                         f"EMA: {strategy_settings['ema']}\n"
                         f"MA: {strategy_settings['ma']}",
                         reply_markup=menu_chancel())


@logger.catch()
async def sending_start_fractal_strategy(strategy_settings, message):
    await message.answer(f"Period: {strategy_settings['period']}\n"
                         f"Stop_loss: {strategy_settings['stop_loss']}\n"
                         f"Take_profit: {strategy_settings['take_profit']}",
                         reply_markup=menu_chancel())


@logger.catch()
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
    dp.register_message_handler(get_period_fractal, state=FractalStrategyState.period)
    dp.register_callback_query_handler(stop_loss_selection_fractal, state=FractalStrategyState.stop_loss_selection)
    dp.register_message_handler(get_stop_loss_fractal, state=FractalStrategyState.stop_loss)
    dp.register_callback_query_handler(take_profit_selection_fractal, state=FractalStrategyState.take_profit_selection)
    dp.register_message_handler(get_take_profit_fractal, state=FractalStrategyState.take_profit)


if __name__ == '__main__':
    logger.info('Running ema_command_search.py from module telegram_api/handlers')