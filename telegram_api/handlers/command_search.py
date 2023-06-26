import asyncio
import datetime

from loguru import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from database.database import db_write
from telegram_api.handlers.keyboards import search_menu_exchange, search_menu_ticker, search_menu_time_frame
from telegram_api.handlers.other_commands import command_start
from telegram_api.handlers.state_machine import CoinInfoStates
from telegram_api.interaction_exchange.search_signal import output_signals
from telegram_api.interaction_exchange.time_frames_editing import get_timeout_response, get_waiting_time


@logger.catch()
async def command_chancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await message.reply('Сброс')
    await state.finish()
    await command_start(message)


@logger.catch()
async def command_search_signal(message: types.Message):
    await CoinInfoStates.exchange_type.set()
    await message.reply('На какой секции биржи искать сигналы?', reply_markup=search_menu_exchange())


@logger.catch()
async def coin_info_exchange_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['exchange_type'] = callback.data.upper()
    await CoinInfoStates.next()
    await callback.message.answer('Введи тикер инструмента', reply_markup=search_menu_ticker())


@logger.catch()
async def coin_info_coin_name(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['coin_name'] = callback.data.upper()
    await CoinInfoStates.next()
    await callback.message.answer('Введи тайм-фрейм данных', reply_markup=search_menu_time_frame())


@logger.catch()
async def coin_info_time_frame(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['time_frame'] = callback.data
    await CoinInfoStates.next()
    await callback.message.answer('Введи период быстрой экспоненциальной скользящей средней')


@logger.catch()
async def coin_info_ema(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ema'] = message.text
    await CoinInfoStates.next()
    await message.answer('Введи период медленной простой скользящей средней')


@logger.catch()
async def coin_info_ma(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ma'] = message.text

    await CoinInfoStates.next()
    await message.answer(f"Начинаю поиск сигналов на бирже Binance\n"
                         f"Параметры поиска:\n"
                         f"Секция биржи: {data['exchange_type']}\n"
                         f"Тикер инструмента: {data['coin_name']}\n"
                         f"Тайм-фрейм: {data['time_frame']}\n"
                         f"EMA: {data['ema']}\n"
                         f"MA: {message.text}")

    signal = await coin_info_signal(message, data)

    await message.answer(f"Получен сигнал {signal} на инструменте {data['coin_name']}, "
                         f"тайм-фрейм: {data['time_frame']}\n"
                         f"Скользящие средние:\n"
                         f"Быстрая - {data['ema']}, медленная - {data['ma']}")

    await state.finish()
    await state.reset_state()


@logger.catch()
async def coin_info_signal(message, data):
    exchange_type, coin_name, time_frame, ema, ma = \
        data['exchange_type'], data['coin_name'], data['time_frame'], int(data['ema']), int(data['ma'])

    timeout_seconds = get_timeout_response(time_frame)
    logger.info(f"Интервал в секундах: {timeout_seconds}")

    while True:
        now = datetime.datetime.now()

        logger.info(f'Поиск сигнала {now}\n'
                    f'На symbol={coin_name}, time_frame={time_frame}, period_fast={ema}, period_slow={ma}')

        waiting_time_seconds = get_waiting_time(now, time_frame)
        seconds_passed = timeout_seconds - waiting_time_seconds

        if 0 <= seconds_passed < 10 or waiting_time_seconds == 0:
            logger.info(f'Отправка запроса на сервер.')

            result = output_signals(exchange_type=exchange_type, symbol=coin_name, timeframe=time_frame,
                                    period_fast=ema, period_slow=ma)
            logger.info(f'Получен сигнал: {result}')

            if result:
                db_write(
                    date_time=now.strftime("%Y-%m-%d %H:%M:%S"),
                    client_id=message.from_user.id,
                    user_name=message.from_user.username,
                    exchange=exchange_type,
                    ticker=coin_name,
                    period=time_frame,
                    ema=ema,
                    ma=ma,
                    signal=result
                )

                return result

        else:
            await asyncio.sleep(waiting_time_seconds)
            continue

        logger.info(f'Ожидаем закрытия периода {time_frame}.')
        await asyncio.sleep(timeout_seconds)
        logger.info(f'Закрытие периода {time_frame}.')


@logger.catch()
def register_handlers_commands_signal(dp: Dispatcher):
    dp.register_message_handler(command_search_signal, commands=['search'], state=None)
    dp.register_callback_query_handler(coin_info_exchange_type, state=CoinInfoStates.exchange_type)
    dp.register_callback_query_handler(coin_info_coin_name, state=CoinInfoStates.coin_name)
    dp.register_callback_query_handler(coin_info_time_frame, state=CoinInfoStates.time_frame)
    dp.register_message_handler(coin_info_ema, state=CoinInfoStates.ema)
    dp.register_message_handler(coin_info_ma, state=CoinInfoStates.ma)
    dp.register_message_handler(command_chancel, commands=['сброс'], state='*')
    dp.register_message_handler(command_chancel, Text(equals='сброс', ignore_case=True), state='*')


if __name__ == '__main__':
    logger.info('Запущен command_search.py из модуля telegram_api/handlers')
