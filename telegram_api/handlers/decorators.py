from loguru import logger

from exchanges.bybit_api.coin_info import get_instrument_info_bybit
from exchanges.client.client import Client
from telegram_api.handlers.keyboards import menu_chancel


@logger.catch()
def check_float(func):
    async def wrapper(message, state):
        try:
            _ = float(message.text)
            await func(message, state)
        except ValueError:
            await message.answer('Неверное число!\n'
                                 'Должно быть целым или вещественным числом.')

    return wrapper


@logger.catch()
def check_int(func):
    async def wrapper(message, state):
        try:
            _ = int(message.text)
            await func(message, state)
        except ValueError:
            await message.answer('Неверное число!\n'
                                 'Число должно быть целым. ')

    return wrapper


@logger.catch()
def deposit_verification(func):
    async def wrapper(message, state):
        async with state.proxy() as data:
            client_depo = Client(data['exchange'], data['exchange_type']).get_balance
            data['client_depo'] = client_depo
        if float(client_depo) > 0:
            await func(message, state)
        else:
            await message.answer(f'На депозите нет свободных средств: {client_depo} USDT', reply_markup=menu_chancel())

    return wrapper


@logger.catch()
def price_verification(func):
    async def wrapper(message, state):
        user_price = float(message.text)
        async with state.proxy() as data:
            tick_size = data['coin_info']['result']['list'][0]['priceFilter'].get('tickSize')
        accuracy_tick_size = len(tick_size.split('.')[1])
        accuracy_price = len(str(user_price).split('.')[1])
        if accuracy_price <= accuracy_tick_size:
            await func(message, state)
        else:
            await message.answer(f'Неверно указана цена. Шаг цены равен: {tick_size} USDT')

    return wrapper


@logger.catch()
def checking_feasibility_strategy(func):
    async def wrapper(message, state):
        async with state.proxy() as data:
            base_precision = data['coin_info']['result']['list'][0]['lotSizeFilter'].get('basePrecision')
            range_price = float(data['upper_price']) - float(data['lower_price'])
            grid_spacing = range_price / int(data['mesh_threads'])
            data['order_book'] = [float(data['lower_price']) + num * grid_spacing for num in
                                  range(int(data['mesh_threads']))]
            deposit_grid = float(data['client_depo']) * float(data['percentage_deposit']) / 100
            data['order_book'] = deposit_grid
            transaction_cost = deposit_grid / int(data['mesh_threads'])
            data['transaction_cost'] = transaction_cost
        if transaction_cost / float(data['upper_price']) > float(base_precision):
            await func(message, state)
        else:
            await message.answer(f"Не хватает выделенного депозита для сетки.\n"
                                 f"Величина лота на ордер: {transaction_cost / float(data['upper_price'])}\n"
                                 f"меньше минимально возможной: {base_precision}\n"
                                 f"Пересмотрите параметры сетки.", reply_markup=menu_chancel())

    return wrapper


@logger.catch()
def validation_data(func):
    async def wrapper(message, state):
        async with state.proxy() as data:
            if float(data['upper_price']) > float(data['start_price']) > float(data['lower_price']):
                await func(message, state)
            else:
                await message.answer(f"Проверьте корректность введенных параметров сетки.\n"
                                     f"Верхняя цена сетки: {data['upper_price']}\n"
                                     f"Нижняя цена сетки: {data['lower_price']}\n"
                                     f"Цена запуска бота: {data['start_price']}\n", reply_markup=menu_chancel())

    return wrapper


@logger.catch()
def check_coin_name(func):
    async def wrapper(message, state):
        if message.text.upper() in [elem['symbol'] for elem in get_instrument_info_bybit()['result']['list']]:
            await func(message, state)
        else:
            await message.answer(f"Проверьте корректность введенного названия тикера - {message.text}",
                                 reply_markup=menu_chancel())
    return wrapper


if __name__ == '__main__':
    logger.info('Running decorators.py from module telegram_api/handlers')
