from aiogram.dispatcher.filters import Text
from loguru import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from database.database import create_database
from exchanges.bibit_api.coin_info import get_instrument_info
from telegram_api.handlers.decorators import deposit_verification, check_float, price_verification, check_int, \
    validation_data, checking_feasibility_strategy
from telegram_api.handlers.keyboards import menu_exchange, menu_exchange_type, menu_ticker, menu_percentage, \
    menu_chancel
from telegram_api.handlers.state_machine import GridState

_variables = {'ignore_message': False, 'interrupt': False}


@logger.catch()
def ignore_messages(func):
    async def wrapper(message: types.Message, state: FSMContext):
        if not _variables['ignore_message']:
            return await func(message, state)

    return wrapper


@logger.catch()
async def command_chancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        _variables['interrupt'] = True
        await state.finish()
        await message.answer('Остановка бота.')
        logger.info("Получена команда на остановку бота.")


@logger.catch()
async def command_arrange_grid(message: types.Message):
    _variables = {'ignore_message': False, 'interrupt': False}
    await GridState.exchange.set()
    await message.answer('На какой бирже искать сигналы?', reply_markup=menu_exchange())


@logger.catch()
async def change_exchange(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['exchange'] = callback.data.upper()
    await GridState.next()
    await callback.message.answer('На какой секции биржи искать сигналы?', reply_markup=menu_exchange_type())


@logger.catch()
async def change_exchange_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['exchange_type'] = callback.data.upper()
    await GridState.next()
    await callback.message.answer('Введите тикер инструмента', reply_markup=menu_ticker())


@logger.catch()
async def change_coin_name(callback: types.CallbackQuery, state: FSMContext):
    create_database(callback.data)
    async with state.proxy() as data:
        data['coin_name'] = callback.data
        data['coin_info'] = get_instrument_info('spot', data['coin_name'])   # сделать выбор типа инструмента
    await GridState.next()
    await callback.message.answer('Какой процент от свободного депозита использовать?', reply_markup=menu_percentage())


@logger.catch()
@deposit_verification
async def change_percentage_deposit(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['percentage_deposit'] = callback.data
    await GridState.next()
    await callback.message.answer('Укажите верхнюю границу цены для сетки.', reply_markup=menu_chancel())


@logger.catch()
@check_float
@price_verification
async def get_upper_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['upper_price'] = float(message.text)
    await GridState.next()
    await message.answer('Укажите нижнюю границу цены для сетки.', reply_markup=menu_chancel())


@logger.catch()
@check_float
@price_verification
async def get_lower_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['lower_price'] = float(message.text)
    await GridState.next()
    await message.answer('Укажите количество "нитей" сетки.', reply_markup=menu_chancel())


@logger.catch()
@check_int
async def get_mesh_threads(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['mesh_threads'] = message.text
    await GridState.next()
    await message.answer('Укажите цену при достижении которой бот начнет свою работу.', reply_markup=menu_chancel())


@logger.catch()
@check_float
@price_verification
@ignore_messages
async def get_start_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['start_price'] = float(message.text)
    _variables['ignore_message'] = True
    await start_grid_strategy(message, state)


@logger.catch()
@validation_data
@checking_feasibility_strategy
async def start_grid_strategy(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer(f"Расставляю ордера согласно параметрам сетки:\n"
                             f"Секция биржи: {data['exchange_type']}\n"
                             f"Тикер инструмента: {data['coin_name']}\n"
                             f"Верхняя граница: {data['upper_price']}\n"
                             f"Нижняя граница: {data['lower_price']}\n"
                             f"Количество нитей: {data['mesh_threads']}\n"
                             f"Цена старта бота: {data['start_price']}\n"
                             f"Используемый депозит: {data['percentage_deposit']}% от свободной суммы\n",
                             reply_markup=menu_chancel())

    logger.info(f"Старт grid_bot.")
    await command_chancel(message, state)
    logger.info(f"Grid_bot остановлен. {data}")


def register_handlers_commands_arrange_grid(dp: Dispatcher):
    dp.register_message_handler(command_arrange_grid, commands=['grid'])
    dp.register_callback_query_handler(command_arrange_grid)
    dp.register_callback_query_handler(change_exchange, state=GridState.exchange)
    dp.register_callback_query_handler(change_exchange_type, state=GridState.exchange_type)
    dp.register_callback_query_handler(change_coin_name, state=GridState.coin_name)
    dp.register_callback_query_handler(change_percentage_deposit, state=GridState.percentage_deposit)
    dp.register_message_handler(get_upper_price, state=GridState.upper_price)
    dp.register_message_handler(get_lower_price, state=GridState.lower_price)
    dp.register_message_handler(get_mesh_threads, state=GridState.mesh_threads)
    dp.register_message_handler(get_start_price, state=GridState.starting_price)
    dp.register_message_handler(command_chancel, commands=['сброс', 'прервать', 'chancel'], state='*')
    dp.register_message_handler(command_chancel, Text(equals=['сброс', 'прервать', 'chancel'], ignore_case=True),
                                state='*')


if __name__ == '__main__':
    logger.info('Running command_arrange_grid.py from module telegram_api/handlers')
