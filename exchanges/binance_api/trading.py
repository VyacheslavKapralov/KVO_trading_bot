import time

from loguru import logger
from binance.error import ClientError
from exchanges.binance_api.connect_binance import connect_um_futures_client, connect_spot_client
from exchanges.binance_api.exchange_data.commission_rate import commission_rate_um_futures
from exchanges.binance_api.exchange_data.exchange_info import exchange_info_um_futures
from exchanges.binance_api.exchange_data.ticker_price import ticker_price_um_futures
from exchanges.binance_api.get_exchange_client_info import Client


class Order:

    def __init__(self, exchange_type: str, name_coin: str):
        self.exchange_type = exchange_type
        self.name_coin = name_coin

    @logger.catch()
    def new_order(self, *args):
        if self.exchange_type == "FUTURES":
            return self._new_order_um_futures(self, args)
        else:
            return self._new_order_spot()

    @logger.catch()
    def get_all_orders(self):
        if self.exchange_type == "FUTURES":
            return self._get_all_orders_um_futures()
        else:
            return self._get_all_orders_spot()

    @logger.catch()
    def get_orders(self):
        if self.exchange_type == "FUTURES":
            return self._get_orders_um_futures()
        else:
            return "self._get_orders_spot()"

    def cancel_all_open_orders(self):
        if self.exchange_type == "FUTURES":
            return self._cancel_all_open_orders_um_futures()
        else:
            return self._cancel_all_open_orders_spot()

    @logger.catch()
    def cancel_open_orders(self):
        if self.exchange_type == "FUTURES":
            return self._cancel_open_order_um_futures()
        else:
            return self._cancel_open_order_spot()

    @logger.catch()
    def _new_order_um_futures(self, side: str, position_side: str, type_position: str, quantity: float,
                              time_in_force: str, price: float = None, stop: float = None) -> dict | str:
        count = 0
        while True:
            try:
                return connect_um_futures_client().new_order(
                    symbol=self.name_coin,
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
    def _new_order_spot(self, side: str, type_position: str, quantity: float, time_in_force: str,
                        price: float) -> dict | str:
        count = 0
        while True:
            try:
                return connect_spot_client().new_order(
                    symbol=self.name_coin,
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
    def _cancel_all_open_orders_um_futures(self) -> dict | str:
        try:
            return connect_um_futures_client().cancel_open_orders(symbol=self.name_coin, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _cancel_open_order_um_futures(self, order_id: int) -> dict | str:
        try:
            return connect_um_futures_client().cancel_order(symbol=self.name_coin, orderId=order_id, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _cancel_all_open_orders_spot(self) -> dict | str:
        try:
            return connect_spot_client().cancel_open_orders(symbol=self.name_coin, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _cancel_open_order_spot(self, order_id: str) -> dict | str:
        try:
            return connect_spot_client().cancel_order(symbol=self.name_coin, orderId=order_id, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _get_all_orders_um_futures(self) -> dict | str:
        try:
            return connect_um_futures_client().get_all_orders(symbol=self.name_coin, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _get_all_orders_spot(self) -> dict | str:
        try:
            return connect_spot_client().get_orders(symbol=self.name_coin, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message

    @logger.catch()
    def _get_orders_um_futures(self) -> dict | str:
        try:
            return connect_um_futures_client().get_orders(symbol=self.name_coin, recvWindow=6000)
        except ClientError as error:
            logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
                        f"error message: {error.error_message}")
            return error.error_message


class Position:

    def __init__(self, exchange_type: str, name_coin: str):
        self.exchange_type = exchange_type
        self.name_coin = name_coin

    @logger.catch()
    def open_position(self, data: str | tuple, percentage_deposit: float) -> str | dict:
        if self.exchange_type == "FUTURES":
            if isinstance(data, str):
                return self._open_position_ema_futures(data, percentage_deposit)
            elif isinstance(data, tuple):
                return self._open_position_fibo_futures(data, percentage_deposit)
        else:
            return ""

    @logger.catch()
    def close_position(self, position_side: str, quantity: float) -> dict | str:
        if self.exchange_type == "FUTURES":
            return self._close_position_futures(self.name_coin, position_side, quantity)
        else:
            return ""

    @logger.catch()
    def _open_position_ema_futures(self, data: str, percentage_deposit: float) -> dict | str | None:
        coin_info = self._get_exchange_info_coin_futures(self.name_coin)
        if isinstance(coin_info, str) or not coin_info:
            return f"Не удалось получить данные по инструменту {self.name_coin}: {coin_info}"
        balance_client = self._get_free_balance_coin_futures(coin_info["quoteAsset"])
        if isinstance(balance_client, str):
            return f"Не удалось получить баланс клиента: {balance_client}"
        ticker_price = ticker_price_um_futures(self.name_coin)
        if isinstance(ticker_price, str) or not ticker_price:
            logger.info(f"Не удалось получить цену инструмента {self.name_coin}: {ticker_price}")
            return f"Не удалось получить цену инструмента {self.name_coin}: {ticker_price}"
        fee = float(commission_rate_um_futures(self.name_coin)['takerCommissionRate'])
        if isinstance(fee, str):
            logger.info(f"Не удалось получить комиссию по инструменту {self.name_coin}: {fee}")
            return f"Не удалось получить комиссию по инструменту {self.name_coin}: {fee}"
        if data == "LONG":
            side = "BUY"
            price = float(ticker_price['price']) * 0.9998
        else:
            side = "SELL"
            price = float(ticker_price['price']) * 1.0002
        rounding_accuracy = self._get_rounding_accuracy(coin_info["filters"][0].get("tickSize"))
        price_round = round(price, rounding_accuracy)
        volume_max = self._get_volume_max(balance_client, coin_info["filters"][1].get("minQty"), percentage_deposit,
                                          price)
        if float(coin_info["filters"][1].get("minQty")) <= volume_max + volume_max * fee:
            order = Order(self.exchange_type, self.name_coin)
            return order.new_order(
                symbol=self.name_coin,
                side=side,
                position_side=data,
                type_position="LIMIT",
                quantity=volume_max,
                time_in_force="GTC",
                price=price_round
            )
        else:
            logger.info("Недостаточно баланса для совершения операции.")
            return "Недостаточно баланса для совершения операции. " \
                   "Увеличьте используемый процент от депозита или пополните депозит."

    @logger.catch()
    def _close_position_futures(self, position_side: str, quantity: float) -> dict | str:
        price = 0
        side = ''
        ticker_price = ticker_price_um_futures(self.name_coin)
        if isinstance(ticker_price, str):
            logger.info(f"Не удалось получить цену инструмента {self.name_coin}: {ticker_price}")
            return f"Не удалось получить цену инструмента {self.name_coin}: {ticker_price}"
        exchange_info = self._get_exchange_info_coin_futures(self.name_coin)
        if isinstance(exchange_info, str):
            return f"Не удалось получить данные по инструменту {self.name_coin}: {exchange_info}"
        if position_side == "SHORT":
            side = "BUY"
            price = float(ticker_price['price']) * 0.9998
        elif position_side == "LONG":
            side = "SELL"
            price = float(ticker_price['price']) * 1.0002
        rounding_accuracy = self._get_rounding_accuracy(exchange_info["filters"][0].get("tickSize"))
        price_round = round(price, rounding_accuracy)
        order = Order(self.exchange_type, self.name_coin)
        return order.new_order(
            symbol=self.name_coin,
            side=side,
            position_side=position_side,
            type_position="LIMIT",
            quantity=quantity,
            time_in_force="GTC",
            price=price_round
        )

    @logger.catch()
    def _open_position_fibo_futures(self, data: str | tuple, percentage_deposit: float) -> dict | str | None:
        coin_info = self._get_exchange_info_coin_futures(self.name_coin)
        if isinstance(coin_info, str) or not coin_info:
            return f"Не удалось получить данные по инструменту {self.name_coin}: {coin_info}"
        balance_client = self._get_free_balance_coin_futures(coin_info["quoteAsset"])
        if isinstance(balance_client, str):
            return f"Не удалось получить баланс клиента: {balance_client}"
        ticker_price = ticker_price_um_futures(self.name_coin)
        if isinstance(ticker_price, str) or not ticker_price:
            logger.info(f"Не удалось получить цену инструмента {self.name_coin}: {ticker_price}")
            return f"Не удалось получить цену инструмента {self.name_coin}: {ticker_price}"
        fee = float(commission_rate_um_futures(self.name_coin)['takerCommissionRate'])
        if isinstance(fee, str):
            logger.info(f"Не удалось получить комиссию по инструменту {self.name_coin}: {fee}")
            return f"Не удалось получить комиссию по инструменту {self.name_coin}: {fee}"
        price, stop_price, take_price = data
        if float(ticker_price['price']) > price:
            side = "BUY"
            position_side = "LONG"
            stop_side = "SELL"
        else:
            position_side = "SHORT"
            side = "SELL"
            stop_side = "BUY"
        rounding_accuracy = self._get_rounding_accuracy(coin_info["filters"][0].get("tickSize"))
        price_round = round(price, rounding_accuracy)
        volume_max = self._get_volume_max(balance_client, coin_info["filters"][1].get("minQty"), percentage_deposit,
                                          price)
        if float(coin_info["filters"][1].get("minQty")) <= volume_max + volume_max * fee:
            order = Order(self.exchange_type, self.name_coin)
            open_order = order.new_order(
                symbol=self.name_coin,
                side=side,
                position_side=position_side,
                type_position="LIMIT",
                quantity=volume_max,
                time_in_force="GTC",
                price=price_round
            )
            stop_order = order.new_order(
                symbol=self.name_coin,
                side=stop_side,
                position_side=position_side,
                type_position="STOP_MARKET",
                quantity=volume_max,
                time_in_force="GTC",
                stop=round(stop_price, rounding_accuracy)
            )
            take_order = order.new_order(
                symbol=self.name_coin,
                side=stop_side,
                position_side=position_side,
                type_position="TAKE_PROFIT_MARKET",
                quantity=volume_max,
                time_in_force="GTC",
                stop=round(take_price, rounding_accuracy)
            )
            return open_order, stop_order, take_order
        else:
            logger.info("Недостаточно баланса для совершения операции.")
            return "Недостаточно баланса для совершения операции. " \
                   "Увеличьте используемый процент от депозита или пополните депозит."

    @logger.catch()
    def _get_exchange_info_coin_futures(self) -> str | dict | None:
        exchange_info = exchange_info_um_futures()
        if isinstance(exchange_info, str):
            logger.info(f"Не удалось получить информацию биржи по инструментам: {exchange_info}")
            return exchange_info
        for symbol in exchange_info["symbols"]:
            if symbol["symbol"] == self.name_coin:
                return symbol

    @logger.catch()
    def _get_free_balance_coin_futures(self, asset_name: str) -> float | str:
        client = Client(self.exchange_type, self.name_coin)
        balances = client.get_balance()
        if isinstance(balances, str):
            logger.info(f"Не удалось получить баланс клиента: {balances}")
            return balances
        for coin in balances:
            if coin["asset"] == asset_name:
                return round(float(coin["crossWalletBalance"]), 2)

    @logger.catch()
    def _get_volume_max(self, balance_client: float, position_min_quantity: str, percentage_deposit: float,
                        price: float) -> float:
        decimal_places = self._get_rounding_accuracy(position_min_quantity)
        return round(balance_client * percentage_deposit / 100 / price, decimal_places)

    @logger.catch()
    def _get_rounding_accuracy(self, tick_size: str) -> int:
        if tick_size.find('.') > 0:
            return tick_size.split('.')[-1].find('1') + 1
        return


if __name__ == '__main__':
    logger.info('Running trading.py from module binance_api')
