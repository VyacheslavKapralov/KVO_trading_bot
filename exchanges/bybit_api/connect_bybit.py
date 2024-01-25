from loguru import logger
from pybit.unified_trading import HTTP
from pybit.exceptions import FailedRequestError, InvalidRequestError

from settings import BybitSettings


@logger.catch()
def connect_bybit(testnet: bool = False) -> object | str:
    bybit_set = BybitSettings()
    try:
        return HTTP(
            testnet=testnet,
            api_key=bybit_set.api_key.get_secret_value(),
            api_secret=bybit_set.secret_key.get_secret_value(),
        )
    except FailedRequestError as error:
        logger.info(f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                    f"error message: {error.message}")
        return error.message
    except InvalidRequestError as error:
        logger.info(f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                    f"error message: {error.message}")
        return error.message


if __name__ == '__main__':
    logger.info('Running connect_bybit.py from module exchange.bybit_api')

