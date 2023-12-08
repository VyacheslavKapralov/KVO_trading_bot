from loguru import logger

from exchanges.binance_api.commission_rate import commission_rate_um_futures
from exchanges.binance_api.ticker_price import ticker_price_um_futures
from exchanges.client_info.client_info import Client
from exchanges.exchange_info.exchange_info import exchange_info_um_futures
from exchanges.trading.order import Order


class Position(Client):

    def __init__(self, strategy: str):
        super(Position, self).__init__()
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
                return self._open_position_ema_futures_biybit(data, percentage_deposit)
            elif self.exchange_type == 'FUTURES' and self.strategy == 'FIBO':
                return self._open_position_fibo_futures_biybit(data, percentage_deposit)
            elif self.exchange_type == 'SPOT' and self.strategy == 'EMA':
                return self._open_position_ema_spot_biybit(data, percentage_deposit)
            elif self.exchange_type == 'SPOT' and self.strategy == 'FIBO':
                return self._open_position_fibo_spot_biybit(data, percentage_deposit)
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
        coin_info = self._get_exchange_info_coin_futures(self.coin_name)
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
            order = Order(self.exchange_type, self.coin_name)
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
        coin_info = self._get_exchange_info_coin_futures(self.coin_name)
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
            order = Order(self.exchange_type, self.coin_name)
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

    def _open_position_fibo_spot_binance(self, data, percentage_deposit):
        pass

    def _open_position_fractal_futures_binance(self, data, percentage_deposit):
        pass

    def _open_position_fractal_spot_binance(self, data, percentage_deposit):
        pass

    def _open_position_ema_futures_biybit(self, data, percentage_deposit):
        pass

    def _open_position_ema_spot_biybit(self, data, percentage_deposit):
        pass

    def _open_position_fibo_futures_biybit(self, data, percentage_deposit):
        pass

    def _open_position_fibo_spot_biybit(self, data, percentage_deposit):
        pass

    def _open_position_fractal_futures_biybit(self, data, percentage_deposit):
        pass

    def _open_position_fractal_spot_biybit(self, data, percentage_deposit):
        pass


    @logger.catch()
    def _close_position_futures_binance(self, position_side: str, quantity: float) -> dict | str:
        price = 0
        side = ''
        ticker_price = ticker_price_um_futures(self.coin_name)
        if isinstance(ticker_price, str):
            logger.info(f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}")
            return f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}"
        exchange_info = self._get_exchange_info_coin_futures(self.coin_name)
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

    def _close_position_spot_binance(self, name_coin, position_side, quantity):
        pass

    def _close_position_futures_bybit(self, name_coin, position_side, quantity):
        pass

    def _close_position_spot_bybit(self, name_coin, position_side, quantity):
        pass

    @logger.catch()
    def _get_exchange_info_coin_futures(self) -> str | dict | None:
        exchange_info = exchange_info_um_futures()
        if isinstance(exchange_info, str):
            logger.info(f"Не удалось получить информацию биржи по инструментам: {exchange_info}")
            return exchange_info
        for symbol in exchange_info["symbols"]:
            if symbol["symbol"] == self.coin_name:
                return symbol

    @logger.catch()
    def _get_free_balance_coin_futures(self, asset_name: str) -> float | str:
        balances = Client.get_balance()
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
    logger.info('Running position.py from module exchanges/trading')
