from loguru import logger

from binance_api.client_information.get_balance import get_balance_futures
from binance_api.exchange_data.exchange_info import exchange_info_futures
from binance_api.exchange_data.ticker_price import ticker_price_futures
from binance_api.trade.commission_rate import commission_rate_futures
from binance_api.trade.new_order import new_order_futures


@logger.catch()
def open_position(coin: str, exchange_type: str, position_side: str, percentage_deposit: float) -> str | dict:
    if exchange_type == "FUTURES":
        return open_position_futures(coin, position_side, percentage_deposit)
    else:
        return ""


@logger.catch()
def open_position_futures(coin: str, position_side: str, percentage_deposit: float) -> dict | str | None:
    quantity_info = get_quantity_max_min_futures(coin)
    if isinstance(quantity_info, str) or not quantity_info:
        return f"Не удалось получить данные по инструменту {coin}: {quantity_info}"
    balance_client = get_free_balance_coin_futures(quantity_info['quote_asset'])
    if isinstance(balance_client, str):
        return f"Не удалось получить баланс клиента: {balance_client}"
    price = ticker_price_futures(coin)
    if isinstance(price, str) or not price:
        return f"Не удалось получить цену инструмента {coin}: {price}"
    fee = float(commission_rate_futures(coin)['takerCommissionRate'])
    if isinstance(fee, str):
        return f"Не удалось получить комиссию по инструменту {coin}: {fee}"
    price = float(price['price'])
    if position_side == "LONG":
        side = "BUY"
        price -= round(price * 0.0002 / float(quantity_info['tick_size'])) * float(quantity_info['tick_size'])
    else:
        side = "SELL"
        price += round(price * 0.0002 / float(quantity_info['tick_size'])) * float(quantity_info['tick_size'])
    volume_max = get_volume_max(balance_client, quantity_info['min_quantity'], percentage_deposit, price)
    if float(quantity_info['min_quantity']) <= volume_max + volume_max * fee:
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
        return "Недостаточно баланса для совершения операции. " \
               "Увеличьте используемый процент от депозита или пополните депозит."


@logger.catch()
def get_quantity_max_min_futures(coin: str) -> str | dict | None:
    exchange_info = exchange_info_futures()
    if isinstance(exchange_info, str):
        return exchange_info
    for symbol in exchange_info["symbols"]:
        if symbol["symbol"] == coin:
            quote_asset = symbol["quoteAsset"]
            max_quantity = symbol["filters"][1].get("maxQty")
            min_quantity = symbol["filters"][1].get("minQty")
            tick_size = symbol["filters"][0].get("tickSize")
            return {'max_quantity': max_quantity, 'min_quantity': min_quantity, 'quote_asset': quote_asset,
                    'tick_size': tick_size}


@logger.catch()
def get_free_balance_coin_futures(asset_name: str) -> float | str:
    balances = get_balance_futures()
    if isinstance(balances, str):
        return balances
    for coin in balances:
        if coin["asset"] == asset_name:
            return round(float(coin["crossWalletBalance"]), 2)


@logger.catch()
def get_volume_max(balance_client: float, position_min_quantity: str, percentage_deposit: float, price: float) -> float:
    decimal_places = len(position_min_quantity.split('.')[-1])
    dec = 10 ** decimal_places
    volume = int(balance_client * percentage_deposit / 100 / price * dec) / dec
    return volume


if __name__ == '__main__':
    logger.info('Running open_position.py from module actions_with_positions')
