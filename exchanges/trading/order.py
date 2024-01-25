import time

from loguru import logger
from binance.error import ClientError
from pybit.exceptions import InvalidRequestError

from exchanges.bybit_api.connect_bybit import connect_bybit
from exchanges.binance_api.connect_binance import connect_um_futures_client, connect_spot_client


class Order:
    def __init__(self, exchange_name: str, exchange_type: str, coin_name: str):
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.coin_name = coin_name

    @logger.catch()
    def new_order(self, *args, **kwargs):
        match self.exchange_name, self.exchange_type:
            case 'BINANCE', 'FUTURES':
                return self._new_order_um_futures_binance(*args, **kwargs)
            case 'BINANCE', 'SPOT':
                return self._new_order_spot_binance()
            case 'BYBIT', 'FUTURES':
                return self._new_order_futures_bybit(*args, **kwargs)
            case 'BYBIT', 'SPOT':
                pass
            case _:
                return ""

    @logger.catch()
    def get_all_orders(self):
        match self.exchange_name, self.exchange_type:
            case 'BINANCE', 'FUTURES':
                return self._get_all_orders_um_futures_binance()
            case 'BINANCE', 'SPOT':
                return self._get_all_orders_spot_binance()
            case 'BYBIT', 'FUTURES':
                pass
            case 'BYBIT', 'SPOT':
                pass
            case _:
                return ""

    @logger.catch()
    def get_orders(self):
        match self.exchange_name, self.exchange_type:
            case 'BINANCE', 'FUTURES':
                return self._get_orders_um_futures_binance()
            case 'BINANCE', 'SPOT':
                return self._get_orders_spot_binance()
            case 'BYBIT', 'FUTURES':
                pass
            case 'BYBIT', 'SPOT':
                pass
            case _:
                return ""

    def cancel_all_open_orders(self):
        match self.exchange_name, self.exchange_type:
            case 'BINANCE', 'FUTURES':
                return self._cancel_all_open_orders_um_futures_binance()
            case 'BINANCE', 'SPOT':
                return self._cancel_all_open_orders_spot_binance()
            case 'BYBIT', 'FUTURES':
                pass
            case 'BYBIT', 'SPOT':
                pass
            case _:
                return ""

    @logger.catch()
    def cancel_open_order(self):
        match self.exchange_name, self.exchange_type:
            case 'BINANCE', 'FUTURES':
                return self._cancel_open_order_um_futures_binance()
            case 'BINANCE', 'SPOT':
                return self._cancel_open_order_spot_binance()
            case 'BYBIT', 'FUTURES':
                pass
            case 'BYBIT', 'SPOT':
                pass
            case _:
                return ""

    @logger.catch()
    def _new_order_um_futures_binance(self, side: str, quantity: float, position_side: str = None,
                                      type_position: str = 'LIMIT', time_in_force: str = 'GTC', price: float = None,
                                      stop: float = None) -> dict | str:
        count = 0
        while True:
            try:
                return connect_um_futures_client().new_position(
                    symbol=self.coin_name,
                    side=side,
                    positionSide=position_side,
                    type=type_position,
                    quantity=quantity,
                    timeInForce=time_in_force,
                    price=price,
                    stopPrice=stop
                )
            except ClientError as error:
                logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                            f"error message: {error.error_message}")
                return error.error_message
            except Exception as e:
                logger.info(f"Не удается создать ордер. Ошибка: {e}")
                if count == 3:
                    return f"Не удалось создать ордер. Ошибка: {e}"
                count += 1
                time.sleep(2)

    @logger.catch()
    def _new_order_spot_binance(self, side: str, type_position: str, quantity: float, time_in_force: str,
                                price: float) -> dict | str:
        count = 0
        while True:
            try:
                return connect_spot_client().new_position(
                    symbol=self.coin_name,
                    side=side,
                    type=type_position,
                    quantity=quantity,
                    timeInForce=time_in_force,
                    price=price
                )
            except ClientError as error:
                logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                            f"error message: {error.error_message}")
                return error.error_message
            except Exception as e:
                logger.info(f"Не удается создать ордер. Ошибка: {e}")
                if count == 3:
                    return f"Не удалось создать ордер. Ошибка: {e}"
                count += 1
                time.sleep(2)

    @logger.catch()
    def _cancel_all_open_orders_um_futures_binance(self) -> dict | str:
        try:
            return connect_um_futures_client().cancel_open_order(symbol=self.coin_name, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _cancel_open_order_um_futures_binance(self, order_id: int) -> dict | str:
        try:
            return connect_um_futures_client().cancel_order(symbol=self.coin_name, orderId=order_id, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _cancel_all_open_orders_spot_binance(self) -> dict | str:
        try:
            return connect_spot_client().cancel_open_order(symbol=self.coin_name, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _cancel_open_order_spot_binance(self, order_id: str) -> dict | str:
        try:
            return connect_spot_client().cancel_order(symbol=self.coin_name, orderId=order_id, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _get_all_orders_um_futures_binance(self) -> dict | str:
        try:
            return connect_um_futures_client().get_all_orders(symbol=self.coin_name, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _get_all_orders_spot_binance(self) -> dict | str:
        try:
            return connect_spot_client().get_orders(symbol=self.coin_name, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _get_orders_um_futures_binance(self) -> dict | str:
        try:
            return connect_um_futures_client().get_orders(symbol=self.coin_name, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _get_orders_spot_binance(self) -> dict | str:
        try:
            return connect_spot_client().get_orders(symbol=self.coin_name, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _new_order_futures_bybit(self, side: str, qty: str, price: str, order_id: str = None, take_profit: str = None,
                                 stop_loss: str = None, stop_type: str = None):
        count = 3
        while count > 0:
            session = connect_bybit()
            if not isinstance(session, str):
                try:
                    return session.place_order(
                        category="linear",
                        symbol=self.coin_name,
                        side=side,
                        orderType="Limit",
                        qty=qty,
                        price=price,
                        takeProfit=take_profit,
                        stopLoss=stop_loss,
                        timeInForce="GTC",
                        orderLinkId=order_id,
                        isLeverage=0,
                        orderFilter="Order",
                        tpslMode='Full',
                        slOrderType=stop_type
                    )
                except InvalidRequestError as error:
                    logger.info(
                        f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                        f"error message: {error.message}")
                    return f'Error code: {error.status_code} - {error.message}'
            count -= 1


if __name__ == '__main__':
    logger.info('Running order.py from module exchanges/trading')
