import time
from loguru import logger
from exchanges.bibit_api.coin_info import get_instrument_info, get_tickers, get_fee
from exchanges.binance_api.commission_rate import commission_rate_um_futures
from exchanges.binance_api.ticker_price import ticker_price_um_futures
from exchanges.client.client import Client
from exchanges.exchange_info.exchange_info import exchange_info_um_futures
from binance.error import ClientError
from pybit.exceptions import InvalidRequestError
from exchanges.bibit_api.connect_bybit import connect_bybit
from exchanges.binance_api.connect_binance import connect_um_futures_client, connect_spot_client


class Position:

    def __init__(self, exchange_name: str, exchange_type: str, coin_name: str, strategy: str):
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.coin_name = coin_name
        self.strategy = strategy

    @logger.catch()
    def open_position(self, data: str | tuple, percentage_deposit: float) -> str | dict:

        if self.exchange_name == 'BINANCE':
            if self.exchange_type == 'FUTURES' and self.strategy == 'EMA':
                return self._open_position_ema_futures_binance(data, percentage_deposit)
            elif self.exchange_type == 'FUTURES' and self.strategy == 'FIBO':
                return self._open_position_fibo_futures_binance(data, percentage_deposit)
            elif self.exchange_type == 'FUTURES' and self.strategy == 'FRACTAL':
                return self._open_position_fractal_futures_binance(data, percentage_deposit)
            elif self.exchange_type == 'SPOT' and self.strategy == 'EMA':
                return self._open_position_ema_spot_binance(data, percentage_deposit)
            elif self.exchange_type == 'SPOT' and self.strategy == 'FIBO':
                return self._open_position_fibo_spot_binance(data, percentage_deposit)
            elif self.exchange_type == 'SPOT' and self.strategy == 'FRACTAL':
                return self._open_position_fractal_spot_binance(data, percentage_deposit)

        elif self.exchange_name == 'BYBIT':
            if self.exchange_type == 'FUTURES' and self.strategy == 'EMA':
                return self._open_position_ema_futures_bybit(data, percentage_deposit)
            elif self.exchange_type == 'FUTURES' and self.strategy == 'FIBO':
                return self._open_position_fibo_futures_bybit(data, percentage_deposit)
            elif self.exchange_type == 'FUTURES' and self.strategy == 'FRACTAL':
                return self._open_position_fractal_futures_bybit(data, percentage_deposit)
            elif self.exchange_type == 'SPOT' and self.strategy == 'EMA':
                return self._open_position_ema_spot_bybit(data, percentage_deposit)
            elif self.exchange_type == 'SPOT' and self.strategy == 'FIBO':
                return self._open_position_fibo_spot_bybit(data, percentage_deposit)
            elif self.exchange_type == 'SPOT' and self.strategy == 'FRACTAL':
                return self._open_position_fractal_spot_bybit(data, percentage_deposit)

        else:
            return ""

    @logger.catch()
    def close_position(self, position_side: str, quantity: float) -> dict | str:
        if self.exchange_name == 'BINANCE':
            if self.exchange_type == 'FUTURES':
                return self._close_position_futures_binance(self.coin_name, position_side, quantity)
            elif self.exchange_type == 'SPOT':
                return self._close_position_spot_binance(self.coin_name, position_side, quantity)
        elif self.exchange_name == 'BYBIT':
            if self.exchange_type == 'FUTURES':
                return self._close_position_futures_bybit(self.coin_name, position_side, quantity)
            elif self.exchange_type == 'SPOT':
                return self._close_position_spot_bybit(self.coin_name, position_side, quantity)
        else:
            return ""

    @logger.catch()
    def _open_position_ema_futures_binance(self, type_position: str, percentage_deposit: float) -> dict | str | None:
        coin_info = self._get_exchange_info_coin_futures_binance(self.coin_name)
        if isinstance(coin_info, str) or not coin_info:
            return f"Не удалось получить данные по инструменту {self.coin_name}: {coin_info}"
        balance_client = self._get_free_balance_coin_futures(coin_info["quoteAsset"])
        if isinstance(balance_client, str):
            return f"Не удалось получить баланс клиента: {balance_client}"
        ticker_price = ticker_price_um_futures(self.coin_name)
        if isinstance(ticker_price, str) or not ticker_price:
            logger.info(f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}")
            return f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}"
        fee = float(commission_rate_um_futures(self.coin_name)['takerCommissionRate'])
        if isinstance(fee, str):
            logger.info(f"Не удалось получить комиссию по инструменту {self.coin_name}: {fee}")
            return f"Не удалось получить комиссию по инструменту {self.coin_name}: {fee}"
        if type_position == "LONG":
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
            order = Order()
            return order.new_order(
                symbol=self.coin_name,
                side=side,
                position_side=type_position,
                type_position="LIMIT",
                quantity=volume_max,
                time_in_force="GTC",
                price=price_round
            )
        else:
            logger.info("Недостаточно баланса для совершения операции.")
            return "Недостаточно баланса для совершения операции. " \
                   "Увеличьте используемый процент от депозита или пополните депозит."

    def _open_position_ema_spot_binance(self, data, percentage_deposit):
        pass

    @logger.catch()
    def _open_position_fibo_futures_binance(self, data: str | tuple, percentage_deposit: float) -> dict | str | None:
        coin_info = self._get_exchange_info_coin_futures_binance()
        if isinstance(coin_info, str) or not coin_info:
            return f"Не удалось получить данные по инструменту {self.coin_name}: {coin_info}"
        balance_client = self._get_free_balance_coin_futures(coin_info["quoteAsset"])
        if isinstance(balance_client, str):
            return f"Не удалось получить баланс клиента: {balance_client}"
        ticker_price = ticker_price_um_futures(self.coin_name)
        if isinstance(ticker_price, str) or not ticker_price:
            logger.info(f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}")
            return f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}"
        fee = float(commission_rate_um_futures(self.coin_name)['takerCommissionRate'])
        if isinstance(fee, str):
            logger.info(f"Не удалось получить комиссию по инструменту {self.coin_name}: {fee}")
            return f"Не удалось получить комиссию по инструменту {self.coin_name}: {fee}"
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
            order = Order()
            open_order = order.new_order(
                symbol=self.coin_name,
                side=side,
                position_side=position_side,
                type_position="LIMIT",
                quantity=volume_max,
                time_in_force="GTC",
                price=price_round
            )
            stop_order = order.new_order(
                symbol=self.coin_name,
                side=stop_side,
                position_side=position_side,
                type_position="STOP_MARKET",
                quantity=volume_max,
                time_in_force="GTC",
                stop=round(stop_price, rounding_accuracy)
            )
            take_order = order.new_order(
                symbol=self.coin_name,
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
    def _open_position_fibo_spot_binance(self, data, percentage_deposit):
        pass

    @logger.catch()
    def _open_position_fractal_futures_binance(self, data, percentage_deposit):
        pass

    @logger.catch()
    def _open_position_fractal_spot_binance(self, data, percentage_deposit):
        pass

    @logger.catch()
    def _open_position_ema_futures_bybit(self, data, percentage_deposit):
        pass

    @logger.catch()
    def _open_position_ema_spot_bybit(self, data, percentage_deposit):
        pass

    @logger.catch()
    def _open_position_fibo_futures_bybit(self, data, percentage_deposit):
        pass

    @logger.catch()
    def _open_position_fibo_spot_bybit(self, data, percentage_deposit):
        pass

    @logger.catch()
    def _open_position_fractal_futures_bybit(self, data, percentage_deposit):
        coin_info = self._get_exchange_info_coin_futures_bybit()
        if isinstance(coin_info, str) or not coin_info:
            return f"Не удалось получить данные по инструменту {self.coin_name}: {coin_info}"
        balance_client = self._get_free_balance_coin_futures(coin_info["quoteAsset"])
        if isinstance(balance_client, str):
            return f"Не удалось получить баланс клиента: {balance_client}"
        ticker_price = get_tickers('linear', self.coin_name)['result']['list'][0]['lastPrice']
        if isinstance(ticker_price, str) or not ticker_price:
            logger.info(f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}")
            return f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}"
        fee = get_fee('linear', self.coin_name)['result']['list'][0]['makerFeeRate']
        if isinstance(fee, str):
            logger.info(f"Не удалось получить комиссию по инструменту {self.coin_name}: {fee}")
            return f"Не удалось получить комиссию по инструменту {self.coin_name}: {fee}"
        price, stop_price, take_price = data
        if float(ticker_price['price']) > price:
            side = "Buy"
            position_side = "LONG"
            stop_side = "Sell"
        else:
            position_side = "SHORT"
            side = "Sell"
            stop_side = "Buy"
        rounding_accuracy = self._get_rounding_accuracy(coin_info["result"]['list'][0]['lotSizeFilter']['qtyStep'])
        price_round = round(price, rounding_accuracy)
        volume_max = self._get_volume_max(
            balance_client,
            coin_info["result"]['list'][0]['lotSizeFilter']['minOrderQty'],
            percentage_deposit,
            price
        )
        if float(coin_info["result"]['list'][0]['lotSizeFilter']['minOrderQty']) <= volume_max + volume_max * fee:
            order = Order()
            open_order = order.new_order(
                side=side,
                qty=volume_max,
                price=price_round
            )
            stop_order = order.new_order(
                symbol=self.coin_name,
                side=stop_side,
                position_side=position_side,
                type_position="STOP_MARKET",
                quantity=volume_max,
                time_in_force="GTC",
                stop=round(stop_price, rounding_accuracy)
            )
            take_order = order.new_order(
                symbol=self.coin_name,
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
    def _open_position_fractal_spot_bybit(self, data, percentage_deposit):
        pass

    @logger.catch()
    def _close_position_futures_binance(self, position_side: str, quantity: float) -> dict | str:
        price = 0
        side = ''
        ticker_price = ticker_price_um_futures(self.coin_name)
        if isinstance(ticker_price, str):
            logger.info(f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}")
            return f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}"
        exchange_info = self._get_exchange_info_coin_futures_binance(self.coin_name)
        if isinstance(exchange_info, str):
            return f"Не удалось получить данные по инструменту {self.coin_name}: {exchange_info}"
        if position_side == "SHORT":
            side = "BUY"
            price = float(ticker_price['price']) * 0.9998
        elif position_side == "LONG":
            side = "SELL"
            price = float(ticker_price['price']) * 1.0002
        rounding_accuracy = self._get_rounding_accuracy(exchange_info["filters"][0].get("tickSize"))
        price_round = round(price, rounding_accuracy)
        order = Order(self.exchange_type, self.coin_name)
        return order.new_order(
            symbol=self.coin_name,
            side=side,
            position_side=position_side,
            type_position="LIMIT",
            quantity=quantity,
            time_in_force="GTC",
            price=price_round
        )

    @logger.catch()
    def _close_position_spot_binance(self, name_coin, position_side, quantity):
        pass

    @logger.catch()
    def _close_position_futures_bybit(self, name_coin, position_side, quantity):
        pass

    @logger.catch()
    def _close_position_spot_bybit(self, name_coin, position_side, quantity):
        pass

    @logger.catch()
    def _get_exchange_info_coin_futures_binance(self) -> str | dict | None:
        exchange_info = exchange_info_um_futures()
        if isinstance(exchange_info, str):
            logger.info(f"Не удалось получить информацию биржи BINANCE по инструментам: {exchange_info}")
            return exchange_info
        for symbol in exchange_info["symbols"]:
            if symbol["symbol"] == self.coin_name:
                return symbol

    @logger.catch()
    def _get_exchange_info_coin_futures_bybit(self):
        coin_info = get_instrument_info(self.exchange_type, self.coin_name)
        if isinstance(coin_info, str):
            logger.info(f"Не удалось получить информацию биржи BYBIT по инструменту {self.coin_name}: {coin_info}")
        return coin_info

    @logger.catch()
    def _get_free_balance_coin_futures(self, asset_name: str) -> float | str:
        balances = Client.get_balance()
        if isinstance(balances, str):
            logger.info(f"Не удалось получить баланс клиента: {balances}")
        return balances
        # for coin in balances:
        #     if coin["asset"] == asset_name:
        #         return round(float(coin["crossWalletBalance"]), 2)

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


class Order(Position):
    def __init__(self):
        super(Position, self).__init__()

    @logger.catch()
    def new_order(self, *args):
        if self.exchange_name == 'BINANCE':
            if self.exchange_type == 'FUTURES':
                return self._new_order_um_futures_binance(self, *args)
            elif self.exchange_type == 'SPOT':
                return self._new_order_spot_binance()
        elif self.exchange_name == 'BYBIT':
            if self.exchange_type == 'FUTURES':
                return self._new_order_um_futures_bybit(self, *args)
            elif self.exchange_type == 'SPOT':
                pass
        else:
            return ""

    @logger.catch()
    def get_all_orders(self):
        if self.exchange_name == 'BINANCE':
            if self.exchange_type == 'FUTURES':
                return self._get_all_orders_um_futures_binance()
            elif self.exchange_type == 'SPOT':
                return self._get_all_orders_spot_binance()
        elif self.exchange_name == 'BYBIT':
            if self.exchange_type == 'FUTURES':
                pass
            elif self.exchange_type == 'SPOT':
                pass
        else:
            return ""

    @logger.catch()
    def get_orders(self):
        if self.exchange_name == 'BINANCE':
            if self.exchange_type == 'FUTURES':
                return self._get_orders_um_futures_binance()
            elif self.exchange_type == 'SPOT':
                return self._get_orders_spot()
        elif self.exchange_name == 'BYBIT':
            if self.exchange_type == 'FUTURES':
                pass
            elif self.exchange_type == 'SPOT':
                pass
        else:
            return ""

    def cancel_all_open_orders(self):
        if self.exchange_name == 'BINANCE':
            if self.exchange_type == 'FUTURES':
                return self._cancel_all_open_orders_um_futures_binance()
            elif self.exchange_type == 'SPOT':
                return self._cancel_all_open_orders_spot_binance()
        elif self.exchange_name == 'BYBIT':
            if self.exchange_type == 'FUTURES':
                pass
            elif self.exchange_type == 'SPOT':
                pass
        else:
            return ""

    @logger.catch()
    def cancel_open_order(self):
        if self.exchange_name == 'BINANCE':
            if self.exchange_type == 'FUTURES':
                return self._cancel_open_order_um_futures_binance()
            elif self.exchange_type == 'SPOT':
                return self._cancel_open_order_spot_binance()
        elif self.exchange_name == 'BYBIT':
            if self.exchange_type == 'FUTURES':
                pass
            elif self.exchange_type == 'SPOT':
                pass
        else:
            return ""

    @logger.catch()
    def _new_order_um_futures_binance(self, side: str, position_side: str, type_position: str, quantity: float,
                                      time_in_force: str, price: float = None, stop: float = None) -> dict | str:
        count = 0
        while True:
            try:
                return connect_um_futures_client().new_order(
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
                return connect_spot_client().new_order(
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
    def _new_order_um_futures_bybit(self, side, qty, price):
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
                        timeInForce="GTC",
                        orderLinkId="future-telebot",
                        isLeverage=0,
                        orderFilter="Order"
                    )
                except InvalidRequestError as error:
                    logger.info(
                        f"Found error status code: {error.status_code}, error resp_headers: {error.resp_headers}, "
                        f"error message: {error.message}")
                    return f'Error code: {error.status_code} - {error.message}'
            count -= 1


if __name__ == '__main__':
    logger.info('Running position.py from module exchanges/trading')
    new_order = Position(exchange_name='BYBIT', exchange_type='FUTURES', coin_name='BTCUSDT', strategy='FRACTAL')
    print(new_order.open_position(data=(44000, 43950, 45000), percentage_deposit=5))
