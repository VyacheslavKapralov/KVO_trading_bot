import asyncio
import datetime

from loguru import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from binance_api.client_information.get_positions import all_positions
from database.database import db_write
from binance_api.strategy import action_choice
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

    await message.reply('Работа бота остановлена. Проверьте инструмент на наличие открытых позиций.')
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
    await callback.message.answer('Какой процент от свободного депозита использовать?')


@logger.catch()
async def coin_info_percentage_deposit(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['percentage_deposit'] = message.text
    await CoinInfoStates.next()
    await message.answer('Введи период экспоненциальной скользящей средней для линии тренда')


@logger.catch()
async def coin_info_trend_line(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['trend_line'] = int(message.text)
    await CoinInfoStates.next()
    await message.answer('Введи период быстрой экспоненциальной скользящей средней')


@logger.catch()
async def coin_info_ema(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ema'] = int(message.text)
    await CoinInfoStates.next()
    await message.answer('Введи период медленной простой скользящей средней')


@logger.catch()
async def coin_info_ma(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ma'] = int(message.text)

    await coin_signal(message, data)
    await state.reset_state()
    await state.finish()


@logger.catch()
async def coin_signal(message, data):

    timeout_seconds = get_timeout_response(data['time_frame'])
    logger.info(f"Интервал: {timeout_seconds} сек.")

    await message.answer(f"Начинаю поиск сигналов на бирже Binance\n"
                         f"Параметры поиска:\n"
                         f"Секция биржи: {data['exchange_type']}\n"
                         f"Тикер инструмента: {data['coin_name']}\n"
                         f"Тайм-фрейм: {data['time_frame']}\n"
                         f"Процент используемого депозита: {data['percentage_deposit']}%\n"
                         f"Линия тренда - экспоненциальная скользящая средняя: {data['trend_line']}\n"
                         f"EMA: {data['ema']}\n"
                         f"MA: {data['ma']}")

    while True:
        positions = tuple(all_positions(data['coin_name'], data['exchange_type']))

        if len(positions) > 1:
            await message.answer(f"На данном активе уже есть две противоположные позиции:\n"
                                 f"{positions}\n"
                                 f"Скорректируйте позиции на инструменте, чтоб бот мог на нем работать. "
                                 f"Можно оставить только одну позицию.")
            return

        now = datetime.datetime.now()

        logger.info(f"Поиск сигнала {now}\n"
                    f"На symbol={data['coin_name']}, exchange_type={data['exchange_type']}, "
                    f"time_frame={data['time_frame']}, percentage_deposit={data['percentage_deposit']}, "
                    f"trend_line={data['trend_line']}, period_fast={data['ema']}, period_slow={data['ma']}")

        waiting_time_seconds = get_waiting_time(now, data['time_frame'])
        seconds_passed = timeout_seconds - waiting_time_seconds

        if 0 <= seconds_passed < 10 or waiting_time_seconds == 0:
            logger.info(f'Отправка запроса на сервер.')

            signal = output_signals(exchange_type=data['exchange_type'], symbol=data['coin_name'],
                                    timeframe=data['time_frame'], period_trend_line=data['trend_line'],
                                    period_fast=data['ema'], period_slow=data['ma'])
            logger.info(f'Получен сигнал: {signal}')

            if signal:
                db_write(
                    date_time=now.strftime("%Y-%m-%d %H:%M:%S"),
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

                flag, position = action_choice(
                    coin=data['coin_name'],
                    exchange_type=data['exchange_type'],
                    position_side=signal,
                    percentage_deposit=float(data['percentage_deposit']),
                    positions=positions)

                if flag:
                    await message.answer(f"Размещен лимитный ордер:\n"
                                         f"По цене {position}")
                else:
                    await message.answer(f"На данном активе уже есть попутная позиция:\n"
                                         f"{position}\n")

        else:
            await asyncio.sleep(waiting_time_seconds)
            continue

        logger.info(f"Ожидаем закрытия периода {data['time_frame']}.")
        await asyncio.sleep(timeout_seconds)
        logger.info(f"Закрытие периода {data['time_frame']}.")


@logger.catch()
def register_handlers_commands_signal(dp: Dispatcher):
    dp.register_message_handler(command_chancel, commands=['сброс'], state='*')
    dp.register_message_handler(command_chancel, Text(equals='сброс', ignore_case=True), state='*')
    dp.register_message_handler(command_search_signal, commands=['search'], state=None)
    dp.register_callback_query_handler(coin_info_exchange_type, state=CoinInfoStates.exchange_type)
    dp.register_callback_query_handler(coin_info_coin_name, state=CoinInfoStates.coin_name)
    dp.register_callback_query_handler(coin_info_time_frame, state=CoinInfoStates.time_frame)
    dp.register_message_handler(coin_info_percentage_deposit, state=CoinInfoStates.percentage_deposit)
    dp.register_message_handler(coin_info_trend_line, state=CoinInfoStates.trend_line)
    dp.register_message_handler(coin_info_ema, state=CoinInfoStates.ema)
    dp.register_message_handler(coin_info_ma, state=CoinInfoStates.ma)


if __name__ == '__main__':
    logger.info('Running command_search.py from module telegram_api/handlers')
