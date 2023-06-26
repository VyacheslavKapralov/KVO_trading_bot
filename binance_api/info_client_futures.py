import json

from loguru import logger
from binance.error import ClientError
from binance_api.connect_binance import connect_um_futures_client


um_futures_client = connect_um_futures_client()


@logger.catch()
def download_info_futures():
    try:
        return um_futures_client.aysnc_download_info(downloadId="1")
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def cancel_batch_orders_futures():
    try:
        return um_futures_client.cancel_batch_order(
            symbol="BTCUSDT", orderIdList=[], origClientOrderIdList=[], recvWindow=2000
        )
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def cancel_open_orders_futures(symbol):
    """Закрытие всех открытых ордеров на инструменте"""

    try:
        return um_futures_client.cancel_open_orders(symbol=symbol, recvWindow=2000)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def cancel_order_futures(symbol, order_id):
    """Закрытие ордера на инструменте"""

    try:
        return um_futures_client.cancel_order(
            symbol=symbol, orderId=order_id, recvWindow=2000
        )
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_all_orders_futures(symbol):
    try:
        return um_futures_client.get_all_orders(symbol=symbol, recvWindow=2000)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_account_futures():
    try:
        return um_futures_client.account(recvWindow=6000)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_account_trades_futures(symbol):
    try:
        return um_futures_client.get_account_trades(symbol=symbol, recvWindow=6000)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_adl_quantile_futures(symbol):
    """Количество открытых позиций по инструменту"""

    try:
        return um_futures_client.adl_quantile(symbol=symbol, recvWindow=6000)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_api_trading_status_futures():
    try:
        return um_futures_client.api_trading_status(recvWindow=6000)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_balance_futures():
    try:
        return um_futures_client.balance(recvWindow=6000)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_commission_rate_futures(symbol):
    try:
        return um_futures_client.commission_rate(symbol=symbol, recvWindow=6000)
    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


@logger.catch()
def get_positions_futures():
    positions_list = []
    try:
        positions = um_futures_client.account(recvWindow=6000)['positions']
        for position in positions:
            if float(position['askNotional']) > 0:
                positions_list.append(position)
            if float(position['bidNotional']) > 0:
                positions_list.append(position)

        return tuple(positions_list)

    except ClientError as error:
        logger.info(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return error.error_message


if __name__ == '__main__':
    logger.info("Запущен binance_api/utility/info_client_futures.py")
    # for elem in um_futures_client.account(recvWindow=6000)['positions']:
    logger.info(get_positions_futures())