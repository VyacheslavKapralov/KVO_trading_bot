from loguru import logger
from binance.error import ClientError
from binance.um_futures import UMFutures

from binance_api.exchange_data.ticker_price import ticker_price_futures
from settings import BinanceSettings


@logger.catch()
def price_calculation(coin: str, exchange_type: str) -> float:
    if exchange_type == "FUTURES":
        return float(ticker_price_futures(coin)['price'])
    else:
        pass


@logger.catch()
def close_position(coin: str, exchange_type: str, position_side: str, quantity: float):
    if position_side == "LONG":
        side = "SELL"
    else:
        side = "BUY"

    price = price_calculation(coin, exchange_type)

    if exchange_type == "FUTURES":
        return close_hedge_position_futures(coin, side, position_side, quantity, price)
    else:
        pass


@logger.catch()
def close_hedge_position_futures(coin: str, side: str, position_side: str, quantity: float, price: float):
    try:
        binance_set = BinanceSettings()
        connect_um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                              secret=binance_set.secret_key.get_secret_value())

        return connect_um_futures_client.new_order(
            symbol=coin,
            side=side,
            positionSide=position_side,
            type="LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            price=price,
        )

    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


if __name__ == '__main__':
    logger.info('Running close_position.py from module actions_with_positions')
