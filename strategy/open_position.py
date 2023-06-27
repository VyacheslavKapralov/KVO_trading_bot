from loguru import logger

from binance_api.client_information.get_balance import get_balance_futures
from binance_api.exchange_data.exchange_info import exchange_info_futures
from binance_api.trade.commission_rate import commission_rate_futures
from binance_api.trade.new_order import new_order_futures


@logger.catch()
def open_position_futures(coin, side: str, position_side: str, price: float, percentage_deposit: float = 0.1):
    position_max_quantity, position_min_quantity, quote_asset = get_quantity_max_min(coin)
    fee = float(commission_rate_futures(coin)['takerCommissionRate'])

    if balance_client := get_free_balance_coin(quote_asset):
        volume_max = get_volume_max(balance_client, position_min_quantity, percentage_deposit, price)

        if float(position_min_quantity) <= volume_max + volume_max * fee:
            return new_order_futures(
                symbol=coin,
                side=side,
                position_side=position_side,
                type_position='LIMIT',
                quantity=volume_max,
                time_in_force="GTC",
                price=price,
                close_position=False)
    else:
        return balance_client


@logger.catch()
def get_quantity_max_min(coin: str):
    exchange_info = exchange_info_futures()

    for symbol in exchange_info["symbols"]:
        if symbol["symbol"] == coin:
            quote_asset = symbol["quoteAsset"]
            for _filter in symbol["filters"]:
                if _filter["filterType"] == "LOT_SIZE":
                    max_quantity = _filter["maxQty"]
                    min_quantity = _filter["minQty"]
                    return max_quantity, min_quantity, quote_asset


@logger.catch()
def get_free_balance_coin(asset_name: str) -> float:
    res = get_balance_futures()
    for coin in res:
        if coin["asset"] == asset_name:
            return round(float(coin["crossWalletBalance"]), 2)


@logger.catch()
def get_volume_max(balance_client, position_min_quantity, percentage_deposit, price) -> float:
    decimal_places = len(position_min_quantity.split('.')[-1])
    dec = 10 ** decimal_places
    return int(balance_client * percentage_deposit / price * dec) / dec


res_lt = {
    'orderId': 8389765605216607009,
    'symbol': 'ETHUSDT',
    'status': 'NEW',
    'clientOrderId': 'TjRjPvvUfALAAk8ITk32MQ',
    'price': '1700.00',
    'avgPrice': '0.00',
    'origQty': '0.010',
    'executedQty': '0.000',
    'cumQty': '0.000',
    'cumQuote': '0.00000',
    'timeInForce': 'GTC',
    'type': 'LIMIT',
    'reduceOnly': False,
    'closePosition': False,
    'side': 'BUY',
    'positionSide': 'LONG',
    'stopPrice': '0.00',
    'workingType': 'CONTRACT_PRICE',
    'priceProtect': False,
    'origType': 'LIMIT',
    'updateTime': 1687861721661
}
