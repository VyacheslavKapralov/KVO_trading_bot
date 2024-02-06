from loguru import logger
from binance.error import ClientError

from exchanges.binance_api.connect_binance import connect_um_futures_client, connect_spot_client
from exchanges.bybit_api.connect_bybit import connect_bybit
from pybit.exceptions import InvalidRequestError


class Client:

    def __init__(self, exchange_name: str = None, exchange_type: str = None):
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type

    @logger.catch()
    def get_positions(self, coin_name: str) -> tuple | str:
        match self.exchange_name, self.exchange_type:
            case 'BINANCE', 'FUTURES':
                return self._get_positions_coin_um_futures_binance(coin_name)
            case 'BINANCE', 'SPOT':
                pass
            case 'BYBIT', 'FUTURES':
                pass
            case 'BYBIT', 'SPOT':
                pass
            case _:
                return ''

    @logger.catch()
    def get_coin_position(self, coin_name: str) -> tuple | str:
        match self.exchange_name, self.exchange_type:
            case 'BINANCE', 'FUTURES':
                pass
            case 'BINANCE', 'SPOT':
                pass
            case 'BYBIT', 'FUTURES':
                pass
            case 'BYBIT', 'SPOT':
                pass
            case _:
                return ''

    @logger.catch()
    def get_balance(self) -> dict | float | str:
        match self.exchange_name, self.exchange_type:
            case 'BINANCE', 'FUTURES':
                return self._get_balance_um_futures_binance()
            case 'BINANCE', 'SPOT':
                return self._get_balance_spot_binance()
            case 'BYBIT', 'LINEAR':
                return self._get_balance_unified_bybit()
            case 'BYBIT', 'SPOT':
                return self._get_balance_unified_bybit()
            case _:
                return ''

    @logger.catch()
    def _get_positions_coin_um_futures_binance(self, coin_name: str) -> tuple | str:
        try:
            positions = connect_um_futures_client().account(recvWindow=10000)['positions']
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message
        all_positions = (position for position in positions if float(position['positionAmt']) != 0)
        return tuple(position for position in all_positions if position.get('symbol') == coin_name)

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
    def _get_balance_unified_bybit(self) -> float | str:
        count = 3
        while count > 0:
            session = connect_bybit()
            if not isinstance(session, str):
                try:
                    balance = session.get_wallet_balance(accountType='UNIFIED', coin='USDT')
                    return round(float(balance['result']['list'][0].get('totalEquity')), 2)
                except InvalidRequestError as error:
                    logger.info(
                        f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                        f"error message: {error.message}")
                    return f'Error code: {error.status_code} - {error.message}'
            count -= 1
        return f"Не удалось получить данные от биржи."

    @logger.catch()
    def _get_balance_financing_bybit(self):
        count = 3
        while count > 0:
            session = connect_bybit()
            if not isinstance(session, str):
                try:
                    balance = session.get_coins_balance(accountType="FUND", coin='USDT')
                    return round(float(balance['result']['balance'][0].get('transferBalance')), 2)
                except InvalidRequestError as error:
                    logger.info(
                        f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                        f"error message: {error.message}")
                    return f'Error code: {error.status_code} - {error.message}'
            count -= 1
        return f"Не удалось получить данные от биржи."


if __name__ == '__main__':
    logger.info('Running get_exchange_client_info.py from module binance_api')
