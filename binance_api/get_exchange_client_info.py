from loguru import logger
from binance.error import ClientError
from binance_api.connect_binance import connect_um_futures_client, connect_spot_client


class Client:

    def __init__(self, exchange_type: str = None, name_coin: str = None):
        self.exchange_type = exchange_type
        self.name_coin = name_coin

    @logger.catch()
    def get_positions(self) -> tuple | str:
        if self.exchange_type == "FUTURES":
            return self._get_positions_coin_um_futures()
        else:
            return ""

    @logger.catch()
    def get_balance(self) -> dict | str:
        if self.exchange_type == "FUTURES":
            return self._get_balance_um_futures()
        else:
            return self._get_balance_spot()

    @logger.catch()
    def _get_positions_coin_um_futures(self) -> tuple | str:
        try:
            positions = connect_um_futures_client().account(recvWindow=10000)['positions']
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message
        all_positions = (position for position in positions if float(position['positionAmt']) != 0)
        return tuple(position for position in all_positions if position.get('symbol') == self.name_coin)

    @logger.catch()
    def _get_balance_um_futures(self) -> dict | str:
        try:
            return connect_um_futures_client().balance(recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _get_balance_spot(self) -> dict | str:
        try:
            return connect_spot_client().balance(recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message


if __name__ == '__main__':
    logger.info('Running get_exchange_client_info.py from module binance_api')
