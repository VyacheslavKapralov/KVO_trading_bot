from loguru import logger
from binance.error import ClientError
from binance_api.connect_binance import connect_um_futures_client, connect_spot_client


@logger.catch()
def get_balance_um_futures() -> dict | str:
    try:
        return connect_um_futures_client().balance(recvWindow=6000)
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


@logger.catch()
def get_balance_spot() -> dict | str:
    try:
        return connect_spot_client().balance(recvWindow=6000)
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


if __name__ == '__main__':
    logger.info('Running get_balance.py from module binance_api/trade')
