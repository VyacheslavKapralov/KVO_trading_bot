from loguru import logger
from binance.error import ClientError
from exchanges.binance_api.connect_binance import connect_um_futures_client


@logger.catch()
def historical_klines_um_futures(symbol: str, timeframe: str) -> dict | str:
    try:
        return connect_um_futures_client().klines(symbol, timeframe)
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


@logger.catch()
def continuous_klines_um_futures(symbol: str, period: str) -> dict | str:
    try:
        return connect_um_futures_client().continuous_klines(symbol, "PERPETUAL", period)
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


if __name__ == '__main__':
    logger.info('Running klines_with_apikey.py from module binance_api')
