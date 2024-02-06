from aiogram.dispatcher.filters import Text
from loguru import logger
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from database.database import create_database
from exchanges.bybit_api.coin_info import get_instrument_info_bybit
from utils.decorators import (
    deposit_verification,
    check_float,
    price_verification,
    check_int,
    validation_data,
    checking_feasibility_strategy,
    check_coin_name,
)
from telegram_api.handlers.keyboards import (
    menu_exchange,
    menu_exchange_type,
    menu_percentage,
    menu_chancel,
)
from telegram_api.handlers.state_machine import GridState

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
        await command_arrange_grid(message, state)


@logger.catch()
async def command_arrange_grid(message: types.Message, state: FSMContext):
    await state.reset_state()
    global IGNORE_MESSAGE, INTERRUPT
    IGNORE_MESSAGE = False
    INTERRUPT = False
    await GridState.exchange.set()
    await message.answer('На какой бирже запустить бота?', reply_markup=menu_exchange())


@logger.catch()
async def change_exchange(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['exchange'] = callback.data.upper()
    await GridState.exchange_type.set()
    await callback.message.answer('На какой секции биржи?', reply_markup=menu_exchange_type())


@logger.catch()
async def change_exchange_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        match data['exchange'], callback.data:
            case 'BYBIT', 'FUTURES':
                data['exchange_type'] = 'LINEAR'
            case 'BYBIT', 'SPOT':
                data['exchange_type'] = 'SPOT'
    await GridState.coin_name.set()
    await callback.message.answer('Введите тикер инструмента', reply_markup=menu_chancel())


@logger.catch()
@check_coin_name
async def change_coin_name(message: types.Message, state: FSMContext):
    create_database(message.text)
    async with state.proxy() as data:
        data['coin_name'] = message.text.upper()
        data['coin_info'] = get_instrument_info_bybit(exchange_type=data['exchange_type'].lower(),
                                                      symbol=data['coin_name'])
    await GridState.percentage_deposit.set()
    await message.answer('Какой процент от свободного депозита использовать?', reply_markup=menu_percentage())


@logger.catch()
@deposit_verification
async def change_percentage_deposit(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['percentage_deposit'] = int(callback.data)
    await GridState.upper_price.set()
    await callback.message.answer('Укажите верхнюю границу цены для сетки.', reply_markup=menu_chancel())


@logger.catch()
@check_float
@price_verification
async def get_upper_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['upper_price'] = float(message.text)
    await GridState.lower_price.set()
    await message.answer('Укажите нижнюю границу цены для сетки.', reply_markup=menu_chancel())


@logger.catch()
@check_float
@price_verification
async def get_lower_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['lower_price'] = float(message.text)
    await GridState.mesh_threads.set()
    await message.answer('Укажите шаг сетки.', reply_markup=menu_chancel())


@logger.catch()
@check_int
async def get_mesh_threads(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['mesh_threads'] = int(message.text)
    await GridState.starting_price.set()
    await message.answer('Укажите цену при достижении которой бот начнет свою работу.', reply_markup=menu_chancel())


@logger.catch()
@ignore_check
@check_float
@price_verification
async def get_start_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['start_price'] = float(message.text)
    await result(message, state)


@logger.catch()
async def result(message: types.Message, state: FSMContext):
    global IGNORE_MESSAGE
    IGNORE_MESSAGE = True
    strategy_settings = await state.get_data()
    await sending_start_message(strategy_settings, message)
    await state.finish()
    await set_grid(message, strategy_settings)


@logger.catch()
@validation_data
@checking_feasibility_strategy
async def set_grid(message: types.Message, strategy_settings: dict):
    logger.info(f"Старт grid_bot.")
    await message.answer(f"Старт grid_bot.")
    await message.answer(f"Grid_bot остановлен. {strategy_settings}")
    logger.info(f"Grid_bot остановлен. {strategy_settings}")


@logger.catch()
async def sending_start_message(data, message):
    await message.answer(f"Расставляю сетку ордеров\n"
                         f"Секция биржи: {data['exchange_type']}\n"
                         f"Тикер инструмента: {data['coin_name']}\n"
                         f"Верхняя граница: {data['upper_price']}\n"
                         f"Нижняя граница: {data['lower_price']}\n"
                         f"Шаг сетки: {data['mesh_threads']}\n"
                         f"Цена старта бота: {data['start_price']}\n"
                         f"Используемый депозит: {data['percentage_deposit']}% от свободной суммы\n",
                         reply_markup=menu_chancel())


def register_handlers_commands_arrange_grid(dp: Dispatcher):
    dp.register_message_handler(command_arrange_grid, commands=['grid'])
    dp.register_callback_query_handler(command_arrange_grid)
    dp.register_callback_query_handler(change_exchange, state=GridState.exchange)
    dp.register_callback_query_handler(change_exchange_type, state=GridState.exchange_type)
    dp.register_message_handler(change_coin_name, state=GridState.coin_name)
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
