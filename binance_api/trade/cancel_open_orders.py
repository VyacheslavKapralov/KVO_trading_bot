from loguru import logger
from binance.error import ClientError
from binance_api.connect_binance import connect_um_futures_client, connect_spot_client


@logger.catch()
def cancel_all_open_orders_um_futures(symbol: str) -> dict | str:
    try:
        return connect_um_futures_client().cancel_open_orders(symbol=symbol, recvWindow=6000)
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


@logger.catch()
def cancel_open_order_um_futures(symbol: str, order_id: int) -> dict | str:
    try:
        return connect_um_futures_client().cancel_order(symbol=symbol, orderId=order_id, recvWindow=6000)
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


@logger.catch()
def cancel_all_open_orders_spot(symbol: str) -> dict | str:
    try:
        return connect_spot_client().cancel_open_orders(symbol=symbol, recvWindow=6000)
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


@logger.catch()
def cancel_open_order_spot(symbol: str, order_id: str) -> dict | str:
    try:
        return connect_spot_client().cancel_order(symbol=symbol, orderId=order_id, recvWindow=6000)
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


if __name__ == '__main__':
    logger.info('Running cancel_open_orders.py from module binance_api/trade')
