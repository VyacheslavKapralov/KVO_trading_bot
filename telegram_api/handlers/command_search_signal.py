import asyncio
import datetime

from loguru import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from database.database import db_write, create_database
from exchanges.client.client import Client
from exchanges.trading.action_with_positions import launch_strategy
from exchanges.working_with_data.time_frames_editing import get_timeout_response, get_waiting_time
from strategies.signal_ema import output_signals_ema
from strategies.signal_fractals import fractal_strategy
from telegram_api.handlers.command_arrange_grid import command_chancel
from telegram_api.handlers.decorators import check_int, deposit_verification, check_float, check_coin_name
from telegram_api.handlers.keyboards import menu_exchange, menu_exchange_type, menu_ticker, menu_time_frame, \
    menu_percentage, menu_chancel, menu_strategy, menu_price_stop, menu_rollback
from telegram_api.handlers.state_machine import EmaStrategyState, StrategyState, FractalStrategyState

# _variables = {'ignore_message': False, 'interrupt': False}
IGNORE_MESSAGE = False
INTERRUPT = False


def ignore_check(func):
    async def wrapper(message, state):
        global IGNORE_MESSAGE
        if not IGNORE_MESSAGE:
            return await func(message, state)

    return wrapper


@logger.catch()
async def command_chancel(message: types.Message, state: FSMContext):
    global INTERRUPT
    INTERRUPT = True
    current_state = await state.get_state()
    if current_state:
        await state.finish()
        logger.info("Получена команда на остановку бота.")
        await message.answer('Остановка бота.')


@logger.catch()
async def go_back_to_previous_state(state: FSMContext):
    prev_state = await state.get_state()
    if prev_state:
        await state.set_state(prev_state)


@logger.catch()
async def command_new_bot(message: types.Message, state: FSMContext):
    prev_state = await state.get_state()
    if prev_state:
        await state.finish()
        await message.answer('Запускаю еще одного бота.')
    else:
        await command_search_signal(message, state)


@logger.catch()
async def command_search_signal(message: types.Message, state: FSMContext):
    await state.reset_state()
    global IGNORE_MESSAGE, INTERRUPT
    IGNORE_MESSAGE = False
    INTERRUPT = False
    # _variables = {'ignore_message': False, 'interrupt': False}
    await StrategyState.strategy.set()
    await message.answer('Выберите стратегию', reply_markup=menu_strategy())


@logger.catch()
async def strategy(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['strategy'] = callback.data
    await StrategyState.exchange.set()
    await callback.message.answer('На какой бирже искать сигналы?', reply_markup=menu_exchange())


@logger.catch()
async def change_exchange(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['exchange'] = callback.data.upper()
    await StrategyState.exchange_type.set()
    await callback.message.answer('На какой секции биржи искать сигналы?', reply_markup=menu_exchange_type())


@logger.catch()
async def change_exchange_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['exchange_type'] = callback.data.upper()
    await StrategyState.coin_name.set()
    await callback.message.answer('Введите тикер инструмента', reply_markup=menu_chancel())


@logger.catch()
@check_coin_name
async def change_coin_name(message: types.Message, state: FSMContext):
    create_database(message.text.upper())
    async with state.proxy() as strategy_settings:
        strategy_settings['coin_name'] = message.text.upper()
    await StrategyState.time_frame.set()
    await message.answer('Выберите тайм-фрейм данных', reply_markup=menu_time_frame())


@logger.catch()
async def change_time_frame(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['time_frame'] = callback.data
    await StrategyState.percentage_deposit.set()
    await callback.message.answer('Какой процент от свободного депозита использовать?', reply_markup=menu_percentage())


@logger.catch()
async def change_percentage_deposit(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['percentage_deposit'] = int(callback.data)
    if strategy_settings['strategy'] == 'EMA':
        await callback.message.answer('Введите период стоп линии основанной на экспоненциальной скользящей средней',
                                      reply_markup=menu_chancel())
        await EmaStrategyState.stop_line.set()
    elif strategy_settings['strategy'] == 'FRACTAL':
        await callback.message.answer('Задайте период фракталов', reply_markup=menu_chancel())
        await FractalStrategyState.period.set()
    else:
        await callback.message.answer('В разработке...')
        await command_chancel(callback.message, state)


@logger.catch()
@check_int
async def get_ema_stop_period(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['stop_line'] = int(message.text)
    await EmaStrategyState.ema.set()
    await message.answer('Введите период быстрой экспоненциальной скользящей средней', reply_markup=menu_chancel())


@logger.catch()
@check_int
async def get_ema_period(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['ema'] = int(message.text)
    await EmaStrategyState.ma.set()
    await message.answer('Введите период медленной простой скользящей средней', reply_markup=menu_chancel())


@logger.catch()
@ignore_check
@check_int
async def get_ma_period(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['ma'] = int(message.text)
    await add_client(message, state)


@logger.catch()
@check_int
async def get_period_fractal(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['period'] = int(message.text)
    await message.answer('Нужно применять откат цены от цены последнего фрактала?', reply_markup=menu_rollback())
    await FractalStrategyState.rollback.set()


@logger.catch()
async def get_rollback_fractal(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['rollback'] = callback.data
    if callback.data == 'usdt':
        await callback.message.answer('Введите на сколько USDT планируется откат', reply_markup=menu_chancel())
        await FractalStrategyState.rollback_num.set()
    elif callback.data == 'percent':
        await callback.message.answer('Введите на сколько процентов планируется откат', reply_markup=menu_chancel())
        await FractalStrategyState.rollback_num.set()
    else:
        await callback.message.answer('В чем измерять размер stop-loss?', reply_markup=menu_price_stop())
        await FractalStrategyState.stop_loss_selection.set()


@logger.catch()
@check_float
async def get_rollback_num_fractal(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['rollback_num'] = float(message.text)
    await message.answer('В чем измерять размер stop-loss?', reply_markup=menu_price_stop())
    await FractalStrategyState.stop_loss_selection.set()


@logger.catch()
async def stop_loss_selection_fractal(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['stop_loss_selection'] = callback.data
        strategy_settings['stop_loss'] = f"atr period = {strategy_settings['period']}"
    if callback.data == 'percent' or callback.data == 'usdt':
        await callback.message.answer('Введите размер stop-loss')
        return await FractalStrategyState.stop_loss.set()
    await callback.message.answer('В чем измерять размер take-profit?', reply_markup=menu_price_stop())
    await FractalStrategyState.take_profit_selection.set()


@logger.catch()
async def get_stop_loss_fractal(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['stop_loss'] = float(message.text)
    await FractalStrategyState.take_profit_selection.set()
    await message.answer('В чем измерять размер take-profit?', reply_markup=menu_price_stop())


@logger.catch()
async def take_profit_selection_fractal(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['take_profit_selection'] = callback.data
    if callback.data == 'percent' or callback.data == 'usdt':
        await callback.message.answer('Введите размер take-profit')
        return await FractalStrategyState.take_profit.set()
    await callback.message.answer('Введите множитель (целое число) значения ATR для установки take-profit')
    await FractalStrategyState.multiplicity_atr.set()


@logger.catch()
@check_int
@ignore_check
async def get_multiplicity_atr_fractal(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['take_profit'] = f'atr * {message.text}'
        strategy_settings['multiplicity_atr'] = int(message.text)
    await add_client(message, state)


@logger.catch()
@ignore_check
async def get_take_profit_fractal(message: types.Message, state: FSMContext):
    async with state.proxy() as strategy_settings:
        strategy_settings['take_profit'] = float(message.text)
    await add_client(message, state)


@logger.catch()
async def add_client(message: types.Message, state: FSMContext):
    global IGNORE_MESSAGE
    IGNORE_MESSAGE = True
    async with state.proxy() as strategy_settings:
        await sending_start_message(strategy_settings, message)
    await state.finish()
    if strategy_settings['strategy'] == 'EMA':
        await search_ema_signal(message, state, strategy_settings)
    elif strategy_settings['strategy'] == 'FRACTAL':
        await search_fractal_signal(message, state, strategy_settings)


@logger.catch()
async def search_ema_signal(message, state, strategy_settings):
    current_position_last = {'position': None}
    global INTERRUPT
    while not INTERRUPT:
        now_time = datetime.datetime.now()
        waiting_time_seconds = get_waiting_time(now_time, strategy_settings['time_frame'])
        await asyncio.sleep(waiting_time_seconds)
        await sending_start_ema_strategy(strategy_settings, message)
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
            success, order = launch_strategy(strategy_settings)
            if success:
                logger.info(f"Ордер: {order}")
                await message.answer(f"Открыт ордер: \n{order}")
                db_write(
                    date_time=now_time.strftime("%Y-%m-%d %H:%M:%S"),
                    user_name=message.from_user.username,
                    exchange=strategy_settings['exchange'],
                    exchange_type=strategy_settings['exchange_type'],
                    strategy=strategy_settings['strategy'],
                    ticker=strategy_settings['coin_name'],
                    period=strategy_settings['time_frame'],
                    signal=signal,
                    position=order
                )
            elif isinstance(order, str):
                await message.answer(order)

    logger.info("Поиск сигналов остановлен.")
    await message.answer("Поиск сигналов остановлен.")


@logger.catch()
async def search_fractal_signal(message, state, strategy_settings):
    client = Client(strategy_settings['exchange'], strategy_settings['exchange_type'], strategy_settings['coin_name'])
    await sending_start_fractal_strategy(strategy_settings, message)
    global INTERRUPT
    while not INTERRUPT:
        current_position_last = client.get_coin_position()
        now_time = datetime.datetime.now()
        waiting_time_seconds = get_waiting_time(now_time, strategy_settings['time_frame'])
        if current_position_last:
            await asyncio.sleep(waiting_time_seconds)
            continue
        success, order = fractal_strategy(strategy_settings)
        if isinstance(order, str):
            await message.answer(order)

        elif success and isinstance(order, list):
            logger.info(f"Ордер: {order}")
            await message.answer(f"Размещен лимитный ордер:\n{order}")
            db_write(
                date_time=now_time.strftime("%Y-%m-%d %H:%M:%S"),
                user_name=message.from_user.username,
                exchange=strategy_settings['exchange'],
                exchange_type=strategy_settings['exchange_type'],
                strategy=strategy_settings['strategy'],
                ticker=strategy_settings['coin_name'],
                period=strategy_settings['time_frame'],
                signal='success',
                position="\n".join(str(elem) for elem in order)
            )
        elif not success and isinstance(order, str):
            await message.answer(order)

        await asyncio.sleep(waiting_time_seconds)

    await message.answer("Поиск сигналов остановлен.")
    logger.info("Поиск сигналов остановлен.")


@logger.catch()
async def sending_start_message(data, message):
    timeout_seconds = get_timeout_response(data['time_frame'])
    logger.info(f"Старт поиска сигнала по стратегии {data['strategy']}. Период: {timeout_seconds} сек")
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
    await message.answer(f"Получен сигнал '{signal}' на инструменте {strategy_settings['coin_name']},\n"
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
    dp.register_message_handler(command_new_bot, commands='new_bot', state='*')
    dp.register_message_handler(command_new_bot, Text(equals=['новый бот', 'перезапустить', 'new_bot', 'new bot'],
                                                      ignore_case=True), state='*')
    dp.register_message_handler(command_chancel, commands=['сброс', 'прервать', 'chancel'], state='*')
    dp.register_message_handler(command_chancel, Text(equals=['сброс', 'прервать', 'chancel'], ignore_case=True),
                                state='*')
    dp.register_message_handler(command_search_signal, commands=['search'])
    dp.register_callback_query_handler(strategy, state=StrategyState.strategy)
    dp.register_callback_query_handler(change_exchange, state=StrategyState.exchange)
    dp.register_callback_query_handler(change_exchange_type, state=StrategyState.exchange_type)
    dp.register_message_handler(change_coin_name, state=StrategyState.coin_name)
    dp.register_callback_query_handler(change_time_frame, state=StrategyState.time_frame)
    dp.register_callback_query_handler(change_percentage_deposit, state=StrategyState.percentage_deposit)
    dp.register_message_handler(get_ema_stop_period, state=EmaStrategyState.stop_line)
    dp.register_message_handler(get_ema_period, state=EmaStrategyState.ema)
    dp.register_message_handler(get_ma_period, state=EmaStrategyState.ma)
    dp.register_message_handler(get_period_fractal, state=FractalStrategyState.period)
    dp.register_callback_query_handler(get_rollback_fractal, state=FractalStrategyState.rollback)
    dp.register_message_handler(get_rollback_num_fractal, state=FractalStrategyState.rollback_num)
    dp.register_callback_query_handler(stop_loss_selection_fractal, state=FractalStrategyState.stop_loss_selection)
    dp.register_message_handler(get_stop_loss_fractal, state=FractalStrategyState.stop_loss)
    dp.register_callback_query_handler(take_profit_selection_fractal, state=FractalStrategyState.take_profit_selection)
    dp.register_message_handler(get_take_profit_fractal, state=FractalStrategyState.take_profit)
    dp.register_message_handler(get_multiplicity_atr_fractal, state=FractalStrategyState.multiplicity_atr)


if __name__ == '__main__':
    logger.info('Running command_search_signal.py from module telegram_api/handlers')
