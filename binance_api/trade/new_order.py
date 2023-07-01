from loguru import logger
from binance.error import ClientError
from binance.spot import Spot
from binance.um_futures import UMFutures
from settings import BinanceSettings


@logger.catch()
def new_order_futures(symbol: str, side: str, position_side: str, type_position: str, quantity: float,
                      time_in_force: str, price: float):
    try:
        binance_set = BinanceSettings()

        connect_um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                              secret=binance_set.secret_key.get_secret_value())
        return connect_um_futures_client.new_order(
            symbol=symbol,
            side=side,
            positionSide=position_side,
            type=type_position,
            quantity=quantity,
            timeInForce=time_in_force,
            price=price,
        )

    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def new_order_spot(symbol: str, side: str, type_position: str, quantity: float, time_in_force: str,
                   price: float):
    try:
        binance_set = BinanceSettings()

        connect_spot_client = Spot(key=binance_set.api_key.get_secret_value(),
                                   secret=binance_set.secret_key.get_secret_value())
        return connect_spot_client.new_order(
            symbol=symbol,
            side=side,
            type=type_position,
            quantity=quantity,
            timeInForce=time_in_force,
            price=price
        )

    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


if __name__ == '__main__':
    logger.info('Running new_order.py from module binance_api/trade')
