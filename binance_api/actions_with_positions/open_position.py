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
    coin_info = get_exchange_info_coin_futures(coin)
    if isinstance(coin_info, str) or not coin_info:
        return f"Не удалось получить данные по инструменту {coin}: {coin_info}"
    balance_client = get_free_balance_coin_futures(coin_info["quoteAsset"])
    if isinstance(balance_client, str):
        return f"Не удалось получить баланс клиента: {balance_client}"
    ticker_price = ticker_price_futures(coin)
    if isinstance(ticker_price, str) or not ticker_price:
        logger.info(f"Не удалось получить цену инструмента {coin}: {ticker_price}")
        return f"Не удалось получить цену инструмента {coin}: {ticker_price}"
    fee = float(commission_rate_futures(coin)['takerCommissionRate'])
    if isinstance(fee, str):
        logger.info(f"Не удалось получить комиссию по инструменту {coin}: {fee}")
        return f"Не удалось получить комиссию по инструменту {coin}: {fee}"
    if position_side == "LONG":
        side = "BUY"
        price = float(ticker_price['price']) * 0.9998
    else:
        side = "SELL"
        price = float(ticker_price['price']) * 1.0002
    rounding_accuracy = get_rounding_accuracy(coin_info["filters"][0].get("tickSize"))
    price_round = round(price, rounding_accuracy)
    volume_max = get_volume_max(balance_client, coin_info["filters"][1].get("minQty"), percentage_deposit, price)
    if float(coin_info["filters"][1].get("minQty")) <= volume_max + volume_max * fee:
        return new_order_futures(
            symbol=coin,
            side=side,
            position_side=position_side,
            type_position="LIMIT",
            quantity=volume_max,
            time_in_force="GTC",
            price=price_round
        )
    else:
        logger.info("Недостаточно баланса для совершения операции.")
        return "Недостаточно баланса для совершения операции. " \
               "Увеличьте используемый процент от депозита или пополните депозит."


@logger.catch()
def get_exchange_info_coin_futures(coin: str) -> str | dict | None:
    exchange_info = exchange_info_futures()
    if isinstance(exchange_info, str):
        logger.info(f"Не удалось получить информацию биржи по инструментам: {exchange_info}")
        return exchange_info
    for symbol in exchange_info["symbols"]:
        if symbol["symbol"] == coin:
            return symbol


@logger.catch()
def get_free_balance_coin_futures(asset_name: str) -> float | str:
    balances = get_balance_futures()
    if isinstance(balances, str):
        logger.info(f"Не удалось получить баланс клиента: {balances}")
        return balances
    for coin in balances:
        if coin["asset"] == asset_name:
            return round(float(coin["crossWalletBalance"]), 2)


@logger.catch()
def get_volume_max(balance_client: float, position_min_quantity: str, percentage_deposit: float, price: float) -> float:
    decimal_places = get_rounding_accuracy(position_min_quantity)
    return round(balance_client * percentage_deposit / 100 / price, decimal_places)


@logger.catch()
def get_rounding_accuracy(tick_size: str) -> int:
    if tick_size.find('.') > 0:
        return tick_size.split('.')[-1].find('1') + 1
    return


if __name__ == '__main__':
    logger.info('Running open_position.py from module actions_with_positions')
