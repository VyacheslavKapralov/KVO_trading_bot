import asyncio
import datetime

from loguru import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from binance_api.client_information.get_positions import all_positions
from database.database import db_write
from binance_api.strategy import action_choice
from telegram_api.handlers.keyboards import menu_exchange, menu_ticker, menu_time_frame, menu_percentage, menu_chancel
from telegram_api.handlers.other_commands import command_start
from telegram_api.handlers.state_machine import CoinInfoStates
from telegram_api.interaction_exchange.search_signal import output_signals
from telegram_api.interaction_exchange.time_frames_editing import get_timeout_response, get_waiting_time


@logger.catch()
def ignore_messages(func):
    async def wrapper(message: types.Message, state: FSMContext):
        if not ignore_messages:
            return await func(message, state)

    return wrapper


@logger.catch()
def check_int(func):
    async def wrapper(message: types.Message, state: FSMContext):
        try:
            period = int(message.text)
            await func(message, state)
        except ValueError:
            await message.answer('Неверный период!\n'
                                 'Период должен быть целым числом. '
                                 'Введи период быстрой экспоненциальной скользящей средней')
    return wrapper


@logger.catch()
async def command_chancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    global interrupt
    interrupt = True
    await message.reply('Поиск сигналов остановлен. Проверьте инструмент на наличие открытых позиций.')
    await state.finish()
    await command_start(message)
    logger.info("Получена команда на остановку поиска сигналов.")


@logger.catch()
async def command_search_signal(message: types.Message):
    await CoinInfoStates.exchange_type.set()
    await message.reply('На какой секции биржи искать сигналы?', reply_markup=menu_exchange())


@logger.catch()
async def coin_info_exchange_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['exchange_type'] = callback.data.upper()
    await CoinInfoStates.next()
    await callback.message.answer('Введи тикер инструмента', reply_markup=menu_ticker())


@logger.catch()
async def coin_info_coin_name(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['coin_name'] = callback.data.upper()
    await CoinInfoStates.next()
    await callback.message.answer('Введи тайм-фрейм данных', reply_markup=menu_time_frame())


@logger.catch()
async def coin_info_time_frame(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['time_frame'] = callback.data
    await CoinInfoStates.next()
    await callback.message.answer('Какой процент от свободного депозита использовать?', reply_markup=menu_percentage())


@logger.catch()
async def coin_info_percentage_deposit(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['percentage_deposit'] = callback.data
    await CoinInfoStates.next()
    await callback.message.answer('Введи период быстрой экспоненциальной скользящей средней',
                                  reply_markup=menu_chancel())


@logger.catch()
@check_int
async def coin_info_ema(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ema'] = int(message.text)
    await CoinInfoStates.next()
    await message.answer('Введи период медленной простой скользящей средней', reply_markup=menu_chancel())
    global ignore_messages
    ignore_messages = False


@logger.catch()
@ignore_messages
@check_int
async def coin_info_ma(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ma'] = int(message.text)

    global ignore_messages
    ignore_messages = True

    await coin_signal(message, state)


@logger.catch()
async def coin_signal(message, state):
    async with state.proxy() as data:
        pass

    timeout_seconds = get_timeout_response(data['time_frame'])
    logger.info(f"Интервал: {timeout_seconds} сек.")

    await message.answer(f"Начинаю поиск сигналов на бирже Binance\n"
                         f"Параметры поиска:\n"
                         f"Секция биржи: {data['exchange_type']}\n"
                         f"Тикер инструмента: {data['coin_name']}\n"
                         f"Тайм-фрейм: {data['time_frame']}\n"
                         f"Процент используемого депозита: {data['percentage_deposit']}%\n"
                         f"EMA: {data['ema']}\n"
                         f"MA: {data['ma']}",
                         reply_markup=menu_chancel())

    global interrupt
    interrupt = False
    while not interrupt:

        position = tuple(all_positions(data['coin_name'], data['exchange_type']))
        if len(position) > 1:
            await message.answer(f"На данном активе уже есть две противоположные позиции:\n"
                                 f"{position}\n"
                                 f"Скорректируйте позиции на инструменте, чтоб бот мог на нем работать. "
                                 f"Можно оставить только одну позицию.")
            command_chancel(message, state)

        now_time = datetime.datetime.now()

        logger.info(f"Поиск сигнала {now_time}\n"
                    f"На symbol={data['coin_name']}, exchange_type={data['exchange_type']}, "
                    f"time_frame={data['time_frame']}, percentage_deposit={data['percentage_deposit']}, "
                    f"period_fast={data['ema']}, period_slow={data['ma']}")

        waiting_time_seconds = get_waiting_time(now_time, data['time_frame'])
        seconds_passed = timeout_seconds - waiting_time_seconds

        if 0 <= seconds_passed < 10 or waiting_time_seconds == 0:
            logger.info(f'Отправка запроса на сервер.')

            signal = output_signals(exchange_type=data['exchange_type'], symbol=data['coin_name'],
                                    time_frame=data['time_frame'], period_fast=data['ema'], period_slow=data['ma'])
            logger.info(f'Получен сигнал: {signal}')

            if signal:
                db_write(
                    date_time=now_time.strftime("%Y-%m-%d %H:%M:%S"),
                    client_id=message.from_user.id,
                    user_name=message.from_user.username,
                    exchange=data['exchange_type'],
                    ticker=data['coin_name'],
                    period=data['time_frame'],
                    ema=data['ema'],
                    ma=data['ma'],
                    signal=signal
                )

                await message.answer(f"Получен сигнал {signal} на инструменте {data['coin_name']}, "
                                     f"тайм-фрейм: {data['time_frame']}\n"
                                     f"Скользящие средние:\n"
                                     f"Быстрая - {data['ema']}, медленная - {data['ma']}")

                success, position = action_choice(
                    coin=data['coin_name'],
                    exchange_type=data['exchange_type'],
                    position_side=signal,
                    percentage_deposit=float(data['percentage_deposit']),
                    position=position)

                if success:
                    await message.answer(f"Размещен лимитный ордер:\n"
                                         f"По цене {position}")
                else:
                    await message.answer(f"На данном активе уже есть попутная позиция:\n"
                                         f"{position}\n")

        else:
            logger.info(f"Ожидаем закрытия периода {data['time_frame']}.")
            await asyncio.sleep(waiting_time_seconds)
            continue

        await asyncio.sleep(timeout_seconds)
        logger.info(f"Закрытие периода {data['time_frame']}.")

    logger.info("Поиск сигналов прерван.")


@logger.catch()
def register_handlers_commands_signal(dp: Dispatcher):
    dp.register_message_handler(command_chancel, commands=['сброс', 'прервать', 'chancel'], state='*')
    dp.register_message_handler(command_chancel, Text(equals=['сброс', 'прервать', 'chancel'], ignore_case=True),
                                state='*')
    # dp.register_message_handler(ignore_messages_handler, state='*')
    dp.register_message_handler(command_search_signal, commands=['search'], state=None)
    dp.register_callback_query_handler(coin_info_exchange_type, state=CoinInfoStates.exchange_type)
    dp.register_callback_query_handler(coin_info_coin_name, state=CoinInfoStates.coin_name)
    dp.register_callback_query_handler(coin_info_time_frame, state=CoinInfoStates.time_frame)
    dp.register_callback_query_handler(coin_info_percentage_deposit, state=CoinInfoStates.percentage_deposit)
    dp.register_message_handler(coin_info_ema, state=CoinInfoStates.ema)
    dp.register_message_handler(coin_info_ma, state=CoinInfoStates.ma)


if __name__ == '__main__':
    logger.info('Running command_search.py from module telegram_api/handlers')
