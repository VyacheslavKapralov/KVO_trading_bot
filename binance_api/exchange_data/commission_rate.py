from loguru import logger
from binance.error import ClientError
from binance_api.connect_binance import connect_um_futures_client


@logger.catch()
def commission_rate_um_futures(symbol: str) -> dict | str:
    try:
        return connect_um_futures_client().commission_rate(symbol=symbol, recvWindow=6000)
    except ClientError as error:
        logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                    f"error message: {error.error_message}")
        return error.error_message


if __name__ == '__main__':
    logger.info('Running commission_rate.py from module binance_api/trade')
