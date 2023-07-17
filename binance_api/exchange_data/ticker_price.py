from loguru import logger
from binance.error import ClientError
from binance_api.connect_binance import connect_um_futures_client


@logger.catch()
def ticker_price_um_futures(symbol: str) -> dict | str:
    try:
        return connect_um_futures_client().ticker_price(symbol)
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


if __name__ == '__main__':
    logger.info('Running ticker_price.py from module binance_api/exchange_data')
