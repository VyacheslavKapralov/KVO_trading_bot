import json

from loguru import logger
from binance.error import ClientError
from binance.um_futures import UMFutures

from settings import BinanceSettings


@logger.catch()
def exchange_info_futures():
    try:
        binance_set = BinanceSettings()

        connect_um_futures_client = UMFutures(key=binance_set.api_key.get_secret_value(),
                                              secret=binance_set.secret_key.get_secret_value())

        return connect_um_futures_client.exchange_info()
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


if __name__ == '__main__':
    logger.info('Running exchange_info.py from module binance_api/exchange_data')

    res = exchange_info_futures()

    for symbol in res["symbols"]:
        # print(symbol)
        if symbol["symbol"] == "BTCUSDT":
            for _filter in symbol["filters"]:
                if _filter["filterType"] == "LOT_SIZE":
                    position_min_quantity = float(_filter["maxQty"])
                    position_max_quantity = float(_filter["minQty"])
    # print(position_max_quantity, position_min_quantity)
    # with open(f'DATA.json', 'w') as file:
    #     json.dump(res, file, indent=4)
    #
