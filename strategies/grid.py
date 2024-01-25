import asyncio

from loguru import logger

from exchanges.bybit_api.coin_info import get_tickers_bybit


def open_order():
    return 10000


@logger.catch()
def get_current_price(exchange_type: str, symbol: str) -> float:
    return float(get_tickers_bybit(exchange_type, symbol)['result']['list'][0].get('lastPrice'))


def waiting_start_grid(exchange_type: str, symbol: str, start_price: float):
    current_price = get_current_price(exchange_type, symbol)
    if start_price * 1.02 < current_price < start_price * 0.98:
        asyncio.sleep(360)
    else:
        return True


def spread_grid(num, order_book):
    while True:
        if waiting_start_grid(num):
            orders = {}
            for price in order_book:
                order = open_order(price)
                orders['price'] = order
            return orders


if __name__ == '__main__':
    logger.info('Running grid.py from module strategies')
