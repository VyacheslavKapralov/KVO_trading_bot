from loguru import logger

from exchanges.bybit_api.coin_info import get_instrument_info_bybit, get_fee_bybit
from exchanges.client.client import Client
from utils.utils import get_rounding_accuracy
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
    async def wrapper(callback, state):
        async with state.proxy() as data:
            client = Client(data['exchange'], data['exchange_type'])
            client_depo = client.get_balance()
            if isinstance(client_depo, str):
                return await callback.message.answer(f"Не удалось получить баланс клиента: {client_depo}",
                                                     reply_markup=menu_chancel())
            data['client_depo'] = client_depo
        if client_depo > 0:
            await func(callback, state)
        else:
            await callback.message.answer(f"На бирже {data['exchange']} нет свободных средств: {client_depo} USDT",
                                          reply_markup=menu_chancel())

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
    async def wrapper(message, data):
        fee = get_fee_bybit('linear', data['coin_name'])
        if isinstance(fee, str):
            return await message.answer(fee, reply_markup=menu_chancel())
        base_precision = float(data['coin_info']['result']['list'][0]['lotSizeFilter'].get('minOrderQty'))
        range_price = data['upper_price'] - data['lower_price']
        number_orders = int(range_price / data['mesh_threads']) + 1
        deposit_grid = data['client_depo'] * data['percentage_deposit'] / 100
        data['orders_book'] = [data['lower_price'] + num * data['mesh_threads'] for num in range(number_orders)]
        volume_usdt = deposit_grid / number_orders
        volume = volume_usdt / data['upper_price']
        volume = round(volume, get_rounding_accuracy(str(base_precision)))
        while volume >= base_precision:
            data['volume'] = volume
            result_fee = sum([volume * price * fee for price in data['orders_book']])
            deposit_required = sum([volume * price for price in data['orders_book']]) + result_fee

            if deposit_required < deposit_grid:
                await func(message, data)
            else:
                volume -= base_precision
        else:
            await message.answer(f"Не хватает выделенного депозита для сетки.\n"
                                 f"Пересмотрите параметры сетки:\n{data}", reply_markup=menu_chancel())

    return wrapper


@logger.catch()
def validation_data(func):
    async def wrapper(message, data):
        if data['upper_price'] > data['start_price'] > data['lower_price']:
            await func(message, data)
        else:
            return await message.answer(f"Проверьте корректность введенных параметров сетки.\n"
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
