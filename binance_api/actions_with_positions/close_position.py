from loguru import logger

from binance_api.exchange_data.exchange_info import exchange_info_futures
from binance_api.exchange_data.ticker_price import ticker_price_futures
from binance_api.trade.new_order import new_order_futures, new_order_spot


@logger.catch()
def close_position(coin: str, exchange_type: str, position_side: str, quantity: float) -> dict | str:
    if exchange_type == "FUTURES":
        return close_position_futures(coin, position_side, quantity)


@logger.catch()
def close_position_futures(coin: str, position_side: str, quantity: float) -> dict | str:
    ticker_price = ticker_price_futures(coin)
    if isinstance(ticker_price, str):
        logger.info(f"Не удалось получить цену инструмента {coin}: {ticker_price}")
        return f"Не удалось получить цену инструмента {coin}: {ticker_price}"
    exchange_info = get_exchange_info_coin_future(coin)
    if isinstance(exchange_info, str):
        return f"Не удалось получить данные по инструменту {coin}: {exchange_info}"
    if position_side == "LONG":
        side = "BUY"
        price = float(ticker_price['price']) * 0.9998
    else:
        side = "SELL"
        price = float(ticker_price['price']) * 1.0002
    rounding_accuracy = get_rounding_accuracy(exchange_info["filters"][0].get("tickSize"))
    price_round = round(price, rounding_accuracy)
    return new_order_futures(
        symbol=coin,
        side=side,
        position_side=position_side,
        type_position="LIMIT",
        quantity=quantity,
        time_in_force="GTC",
        price=price_round
    )


@logger.catch()
def get_exchange_info_coin_future(coin: str) -> str | dict | None:
    exchange_info = exchange_info_futures()
    if isinstance(exchange_info, str):
        logger.info(f"Не удалось получить информацию биржи по инструментам: {exchange_info}")
        return exchange_info
    for symbol in exchange_info["symbols"]:
        if symbol["symbol"] == coin:
            return symbol


@logger.catch()
def get_rounding_accuracy(tick_size: str) -> int:
    if tick_size.find('.') > 0:
        return tick_size.split('.')[-1].find('1') + 1
    return


if __name__ == '__main__':
    logger.info('Running close_position.py from module actions_with_positions')
