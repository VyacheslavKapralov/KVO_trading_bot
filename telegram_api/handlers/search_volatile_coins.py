from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loguru import logger

from strategies.volatile_coins import volatile_coins
from telegram_api.handlers.decorators import check_int
from telegram_api.handlers.keyboards import menu_exchange, menu_exchange_type, menu_chancel, menu_ascending, \
    menu_time_frame, menu_period
from telegram_api.handlers.state_machine import VolatileCoin


@logger.catch()
async def command_chancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.finish()
        logger.info("Получена команда на отмену.")
        await message.answer('Отмена.')


@logger.catch()
async def command_volatile(message: types.Message, state: FSMContext):
    await state.reset_state()
    await VolatileCoin.exchange.set()
    await message.answer('На какой бирже искать монеты?', reply_markup=menu_exchange())


@logger.catch()
async def change_exchange(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as settings:
        settings['exchange'] = callback.data.upper()
    await VolatileCoin.exchange_type.set()
    await callback.message.answer('На какой секции биржи искать?', reply_markup=menu_exchange_type())


@logger.catch()
async def change_exchange_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as settings:
        settings['exchange_type'] = callback.data.upper()
    await VolatileCoin.top_number.set()
    await callback.message.answer('Сколько вывести инструментов?', reply_markup=menu_chancel())


@logger.catch()
@check_int
async def change_top_number(message: types.Message, state: FSMContext):
    async with state.proxy() as settings:
        settings['top_number'] = int(message.text)
    await VolatileCoin.filtration.set()
    await message.answer('Как сортировать монеты?', reply_markup=menu_ascending())


@logger.catch()
async def change_filtration(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as settings:
        settings['ascending'] = callback.data
    await VolatileCoin.time_frame.set()
    await callback.message.answer('На каком тайм-фрейме искать?', reply_markup=menu_time_frame())


@logger.catch()
async def change_time_frame(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as settings:
        settings['time_frame'] = callback.data
    await VolatileCoin.period.set()
    await callback.message.answer('За какой промежуток времени искать?', reply_markup=menu_period())


@logger.catch()
async def change_period(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as settings:
        settings['period'] = callback.data
        await search_volatile_coins(callback.message, settings)
    await state.finish()


@logger.catch()
async def search_volatile_coins(message: types.Message, settings):
    await message.answer("Это займет некоторое время. Ожидайте")
    result = await volatile_coins(settings)
    await message.answer(f"Получены следующие результаты по волатильности")
    for coin, percent in result.items():
        await message.answer(f"{coin}: {percent}%")


@logger.catch()
def register_handlers_commands_volatile(dp: Dispatcher):
    dp.register_message_handler(command_chancel, commands=['сброс', 'прервать', 'chancel'], state='*')
    dp.register_message_handler(command_chancel, Text(equals=['сброс', 'прервать', 'chancel'], ignore_case=True),
                                state='*')
    dp.register_message_handler(command_volatile, commands=['volatile'])
    dp.register_callback_query_handler(change_exchange, state=VolatileCoin.exchange)
    dp.register_callback_query_handler(change_exchange_type, state=VolatileCoin.exchange_type)
    dp.register_message_handler(change_top_number, state=VolatileCoin.top_number)
    dp.register_callback_query_handler(change_filtration, state=VolatileCoin.filtration)
    dp.register_callback_query_handler(change_time_frame, state=VolatileCoin.time_frame)
    dp.register_callback_query_handler(change_period, state=VolatileCoin.period)


if __name__ == '__main__':
    logger.info('Running search_volatile_coins.py from module telegram_api/handlers')
