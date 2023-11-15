from loguru import logger
from binance.error import ClientError
from exchanges.binance_api.connect_binance import connect_um_futures_client


@logger.catch()
def exchange_info_um_futures() -> dict | str:
    try:
        return connect_um_futures_client().exchange_info()
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


if __name__ == '__main__':
    logger.info('Running exchange_info.py from module binance_api/exchange_data')
