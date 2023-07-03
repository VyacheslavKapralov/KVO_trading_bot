from loguru import logger

from binance_api.exchange_data.ticker_price import ticker_price_futures
from binance_api.trade.new_order import new_order_futures, new_order_spot


@logger.catch()
def price_calculation(coin: str, exchange_type: str) -> float:
    if exchange_type == "FUTURES":
        return ticker_price_futures(coin)['price']
    else:
        pass


@logger.catch()
def close_position(coin: str, exchange_type: str, position_side: str, quantity: float):
    price = price_calculation(coin, exchange_type)
    decimal_places = len(price.split('.')[-1])
    price = float(price)

    if position_side == "LONG":
        side = "SELL"
        price += price * 0.0002

    else:
        side = "BUY"
        price -= price * 0.0002

    if exchange_type == "FUTURES":
        return new_order_futures(
            symbol=coin,
            side=side,
            position_side=position_side,
            type_position="LIMIT",
            quantity=quantity,
            time_in_force="GTC",
            price=round(price, decimal_places)
        )
    else:
        return new_order_spot(
            symbol=coin,
            side=side,
            type_position="LIMIT",
            quantity=quantity,
            time_in_force="GTC",
            price=round(price, decimal_places)
        )


if __name__ == '__main__':
    logger.info('Running close_position.py from module actions_with_positions')
