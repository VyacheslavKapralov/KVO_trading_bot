from loguru import logger
from binance.error import ClientError

from exchanges.bibit_api.client_info import get_balance_financing, get_balance_unified_trading
from exchanges.binance_api.connect_binance import connect_um_futures_client, connect_spot_client


class Client:

    def __init__(self, exchange_name: str = None, exchange_type: str = None, coin_name: str = None):
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.coin_name = coin_name

    @logger.catch()
    def get_positions(self) -> tuple | str:
        if self.exchange_name == 'BINANCE':
            if self.exchange_type == 'FUTURES':
                return self._get_positions_coin_um_futures_binance()
            elif self.exchange_type == 'SPOT':
                pass
        elif self.exchange_name == 'BYBIT':
            if self.exchange_type == 'FUTURES':
                pass
            elif self.exchange_type == 'SPOT':
                pass
        else:
            return ""

    @logger.catch()
    def get_coin_position(self) -> tuple | str:
        if self.exchange_name == 'BINANCE':
            if self.exchange_type == 'FUTURES':
                pass
            elif self.exchange_type == 'SPOT':
                pass
        elif self.exchange_name == 'BYBIT':
            if self.exchange_type == 'FUTURES':
                pass
            elif self.exchange_type == 'SPOT':
                pass
        else:
            return ""

    @logger.catch()
    def get_balance(self) -> dict | str:
        if self.exchange_name == 'BINANCE':
            if self.exchange_type == 'FUTURES':
                return self._get_balance_um_futures_binance()
            elif self.exchange_type == 'SPOT':
                return self._get_balance_spot_binance()
        elif self.exchange_name == 'BYBIT':
            return self._get_balance_bybit()

    @logger.catch()
    def _get_positions_coin_um_futures_binance(self) -> tuple | str:
        try:
            positions = connect_um_futures_client().account(recvWindow=10000)['positions']
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message
        all_positions = (position for position in positions if float(position['positionAmt']) != 0)
        return tuple(position for position in all_positions if position.get('symbol') == self.coin_name)

    @logger.catch()
    def _get_balance_um_futures_binance(self) -> dict | str:
        try:
            return connect_um_futures_client().balance(recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _get_balance_spot_binance(self) -> dict | str:
        try:
            return connect_spot_client().balance(recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _get_balance_bybit(self) -> dict | str:
        if self.exchange_type == 'FUTURES':
            return get_balance_unified_trading('USDT')

            # return get_balance_financing('USDT')
        elif self.exchange_type == 'SPOT':
            return get_balance_unified_trading('USDT')


if __name__ == '__main__':
    logger.info('Running get_exchange_client_info.py from module binance_api')
    # client = Client(exchange_name='BYBIT', exchange_type='FUTURES', coin_name='USDT')
    # print(client.get_balance())
