import asyncio
import datetime
from loguru import logger
from aiogram import types
from aiogram.dispatcher import FSMContext
from exchanges.interaction_exchange.search_signal_fibo import output_signals_fibo
from exchanges.interaction_exchange.time_frames_editing import get_timeout_response, get_waiting_time
from database.database import db_write, create_database
from exchanges.binance_api.action_with_positions import action_choice
from telegram_api.handlers.keyboards import menu_exchange, menu_exchange_type, menu_ticker, menu_time_frame, \
    menu_percentage, menu_chancel
from telegram_api.handlers.state_machine import FiboStrategyState

INTERRUPT = False
IGNORE_MESSAGE = False


@logger.catch()
def ignore_messages(func):
    async def wrapper(message: types.Message, state: FSMContext):
        if not IGNORE_MESSAGE:
            return await func(message, state)

    return wrapper


@logger.catch()
async def fibo_command_chancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    global INTERRUPT
    INTERRUPT = True
    await message.reply('Поиск сигналов остановлен.')
    await state.finish()
    logger.info("Получена команда на остановку поиска сигналов.")


@logger.catch()
async def fibo_command_search_signal(callback: types.CallbackQuery):
    global INTERRUPT, IGNORE_MESSAGE
    INTERRUPT = False
    IGNORE_MESSAGE = False
    await FiboStrategyState.exchange.set()
    await callback.message.reply('На какой бирже искать сигналы?', reply_markup=menu_exchange())


@logger.catch()
async def fibo_change_exchange(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['exchange'] = callback.data.upper()
    await FiboStrategyState.next()
    await callback.message.answer('На какой секции биржи искать сигналы?', reply_markup=menu_exchange_type())


@logger.catch()
async def fibo_change_exchange_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['exchange_type'] = callback.data.upper()
    await FiboStrategyState.next()
    await callback.message.answer('Введи тикер инструмента', reply_markup=menu_ticker())


@logger.catch()
async def fibo_change_coin_name(callback: types.CallbackQuery, state: FSMContext):
    create_database(callback.data)
    async with state.proxy() as data:
        data['coin_name'] = callback.data
    await FiboStrategyState.next()
    await callback.message.answer('Введи тайм-фрейм данных', reply_markup=menu_time_frame())


@logger.catch()
async def fibo_change_time_frame(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['time_frame'] = callback.data
    await FiboStrategyState.next()
    await callback.message.answer('Какой процент от свободного депозита использовать?', reply_markup=menu_percentage())


@logger.catch()
async def fibo_change_percentage_deposit(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['percentage_deposit'] = callback.data
    global IGNORE_MESSAGE
    IGNORE_MESSAGE = True
    await fibo_get_signal(callback, state)


@logger.catch()
async def fibo_get_signal(callback, state):
    async with state.proxy() as data:
        timeout_seconds = get_timeout_response(data['time_frame'])
        logger.info(f"Интервал: {timeout_seconds} сек.")
        await callback.message.answer(f"Начинаю поиск сигналов на бирже {data['exchange']}\n"
                                      f"Параметры поиска:\n"
                                      f"Секция биржи: {data['exchange_type']}\n"
                                      f"Тикер инструмента: {data['coin_name']}\n"
                                      f"Тайм-фрейм: {data['time_frame']}\n"
                                      f"Используемый депозит {data['percentage_deposit']}% от общей суммы\n",
                                      reply_markup=menu_chancel())
    received_order = {}
    while not INTERRUPT:
        now_time = datetime.datetime.now()
        waiting_time_seconds = get_waiting_time(now_time, data['time_frame'])
        seconds_passed = timeout_seconds - waiting_time_seconds
        if 0 <= seconds_passed <= 10:
            logger.info(f'Подсчет данных по стратегии fibo.')
            signal = output_signals_fibo(exchange_type=data['exchange_type'], symbol=data['coin_name'],
                                         time_frame=data['time_frame'], received_order=received_order)
            logger.info(f'Получены данные для ордера: {signal}')
            if signal and isinstance(signal, tuple):
                await callback.message.answer(
                    f"Получены данные для открытия ордера на инструменте {data['coin_name']}, "
                    f"биржа: {data['exchange']},\n"
                    f"Тайм-фрейм: {data['time_frame']}\n"
                    f"Отложенный ордер по цене: {signal[0]}\n"
                    f"Тейк-профит: {signal[1]}\n"
                    f"Стоп-лосс: {signal[2]}")
                success, order = action_choice(
                    symbol=data['coin_name'],
                    exchange_type=data['exchange_type'],
                    signal=signal,
                    percentage_deposit=float(data['percentage_deposit'])
                )
                if success:
                    await callback.message.answer(f"Размещен лимитный ордер:\n"
                                                  f"{order}")
                    db_write(
                        date_time=now_time.strftime("%Y-%m-%d %H:%M:%S"),
                        user_name=callback.message.from_user.username,
                        exchange=data['exchange'],
                        exchange_type=data['exchange_type'],
                        ticker=data['coin_name'],
                        period=data['time_frame'],
                        trend=data['stop_line'],
                        ema=data['ema'],
                        ma=data['ma'],
                        signal=signal,
                        position=f"Price: {order.get('price')}; quantity: {order.get('origQty')}; "
                                 f"type: {order.get('type')}; stop_price: {order.get('stopPrice')}"
                    )
                else:
                    await callback.message.answer(order)
        else:
            await asyncio.sleep(waiting_time_seconds)
            continue
        await asyncio.sleep(waiting_time_seconds)
    await fibo_command_chancel(callback.message, state)
    logger.info("Поиск сигналов прерван.")


if __name__ == '__main__':
    logger.info('Running fibo_command_search.py from module telegram_api/handlers')

# ToDo: 
#  1. После отправки ордера на биржу, проверка следующей свечи на увеличение максимума или минимума. 
#  Последующая корректировка ордера с учетом изменившегося максимума или минимума. Отмена предыдущего ордера. 
#  2. Возможность открытие нескольких ордеров.
