from loguru import logger

from binance_api.client_information.get_balance import get_balance_futures
from binance_api.exchange_data.exchange_info import exchange_info_futures
from binance_api.exchange_data.ticker_price import ticker_price_futures
from binance_api.trade.commission_rate import commission_rate_futures
from binance_api.trade.new_order import new_order_futures


@logger.catch()
def price_calculation(coin: str, exchange_type: str) -> str:
    if exchange_type == "FUTURES":
        return ticker_price_futures(coin)['price']
    else:
        pass


@logger.catch()
def open_position(coin: str, exchange_type: str, position_side: str, percentage_deposit: float):
    price = price_calculation(coin, exchange_type)
    decimal_places = len(price.split('.')[-1])
    price = float(price)

    if position_side == "LONG":
        side = "BUY"
        price -= price * 0.0002
    else:
        side = "SELL"
        price += price * 0.0002

    if exchange_type == "FUTURES":
        return open_position_futures(coin, side, position_side, round(price, decimal_places), percentage_deposit)
    else:
        pass


@logger.catch()
def open_position_futures(coin, side: str, position_side: str, price: float, percentage_deposit: float):
    position_max_quantity, position_min_quantity, quote_asset = get_quantity_max_min_futures(coin)
    fee = float(commission_rate_futures(coin)['takerCommissionRate'])

    if balance_client := get_free_balance_coin_futures(quote_asset):
        volume_max = get_volume_max(balance_client, position_min_quantity, percentage_deposit, price)

        if float(position_min_quantity) <= volume_max + volume_max * fee:
            return new_order_futures(
                symbol=coin,
                side=side,
                position_side=position_side,
                type_position="LIMIT",
                quantity=volume_max,
                time_in_force="GTC",
                price=price
            )
    else:
        return balance_client


@logger.catch()
def get_quantity_max_min_futures(coin: str):
    exchange_info = exchange_info_futures()

    for symbol in exchange_info["symbols"]:
        if symbol["symbol"] == coin:
            quote_asset = symbol["quoteAsset"]
            max_quantity = symbol["filters"][1].get("maxQty")
            min_quantity = symbol["filters"][1].get("minQty")
            return max_quantity, min_quantity, quote_asset


@logger.catch()
def get_free_balance_coin_futures(asset_name: str) -> float:
    res = get_balance_futures()
    for coin in res:
        if coin["asset"] == asset_name:
            return round(float(coin["crossWalletBalance"]), 2)


@logger.catch()
def get_volume_max(balance_client, position_min_quantity, percentage_deposit, price) -> float:
    decimal_places = len(position_min_quantity.split('.')[-1])
    dec = 10 ** decimal_places
    return int(balance_client * percentage_deposit / 100 / price * dec) / dec


if __name__ == '__main__':
    logger.info('Running open_position.py from module actions_with_positions')