from loguru import logger
from binance.error import ClientError
from binance.um_futures import UMFutures
from settings import BinanceSettings


@logger.catch()
def close_hedge_position_futures(symbol: str, position_side: str, quantity: float, price: float):
    try:
        binance_set = BinanceSettings()
        connect_um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                              secret=binance_set.secret_key.get_secret_value())
        if position_side == "LONG":
            side = "SELL"
        else:
            side = "BUY"

        return connect_um_futures_client.new_order(
            symbol=symbol,
            side=side,
            positionSide=position_side,
            type="LIMIT",
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
    logger.info('Running close_hedge_position_futures.py from module actions_with_positions')
