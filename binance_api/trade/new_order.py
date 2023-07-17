import time
from loguru import logger
from binance.error import ClientError
from binance_api.connect_binance import connect_um_futures_client, connect_spot_client


@logger.catch()
def new_order_um_futures(symbol: str, side: str, position_side: str, type_position: str, quantity: float,
                         time_in_force: str, price: float) -> dict | str:
    count = 0
    while True:
        try:
            return connect_um_futures_client().new_order(
                symbol=symbol,
                side=side,
                positionSide=position_side,
                type=type_position,
                quantity=quantity,
                timeInForce=time_in_force,
                price=price,
            )
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message
        except Exception as e:
            logger.info(f"Не удается создать ордер. Ошибка: {e}")
            if count == 3:
                return f"Не удалось создать ордер. Ошибка: {e}"
            count += 1
            time.sleep(2)


@logger.catch()
def new_order_spot(symbol: str, side: str, type_position: str, quantity: float, time_in_force: str,
                   price: float) -> dict | str:
    count = 0
    while True:
        try:
            return connect_spot_client().new_order(
                symbol=symbol,
                side=side,
                type=type_position,
                quantity=quantity,
                timeInForce=time_in_force,
                price=price
            )
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message
        except Exception as e:
            logger.info(f"Не удается создать ордер. Ошибка: {e}")
            if count == 3:
                return f"Не удалось создать ордер. Ошибка: {e}"
            count += 1
            time.sleep(2)


if __name__ == '__main__':
    logger.info('Running new_order.py from module binance_api/trade')
