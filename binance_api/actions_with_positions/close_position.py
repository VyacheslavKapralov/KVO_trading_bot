from loguru import logger

from binance_api.exchange_data.exchange_info import exchange_info_futures
from binance_api.exchange_data.ticker_price import ticker_price_futures
from binance_api.trade.new_order import new_order_futures, new_order_spot


@logger.catch()
def price_calculation(coin: str, exchange_type: str) -> dict | None:
    if exchange_type == "FUTURES":
        return ticker_price_futures(coin)


@logger.catch()
def close_position(coin: str, exchange_type: str, position_side: str, quantity: float) -> dict | str:
    if exchange_type == "FUTURES":
        return close_position_futures(coin, position_side, quantity)


@logger.catch()
def close_position_futures(coin: str, position_side: str, quantity: float) -> dict | str:
    price = ticker_price_futures(coin)
    if isinstance(price, str):
        return f"Не удалось получить цену инструмента {coin}: {price}"
    exchange_info = get_exchange_info_coin_future(coin)
    if isinstance(exchange_info, str):
        return f"Не удалось получить данные по инструменту {coin}: {exchange_info}"
    tick_size = float(exchange_info["filters"][0].get("tickSize"))
    price = float(price['price'])
    if position_side == "LONG":
        side = "SELL"
        price += round(price * 0.0002 / tick_size * tick_size)
    else:
        side = "BUY"
        price -= round(price * 0.0002 / tick_size * tick_size)
    return new_order_futures(
        symbol=coin,
        side=side,
        position_side=position_side,
        type_position="LIMIT",
        quantity=quantity,
        time_in_force="GTC",
        price=price
    )


@logger.catch()
def get_exchange_info_coin_future(coin: str) -> str | dict | None:
    exchange_info = exchange_info_futures()
    if isinstance(exchange_info, str):
        return exchange_info
    for symbol in exchange_info["symbols"]:
        if symbol["symbol"] == coin:
            return symbol


if __name__ == '__main__':
    logger.info('Running close_position.py from module actions_with_positions')
