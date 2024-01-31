from loguru import logger
from exchanges.bybit_api.coin_info import get_instrument_info_bybit, get_tickers_bybit
from exchanges.binance_api.ticker_price import ticker_price_um_futures
from exchanges.trading.order import Order


class Position:

    def __init__(self, exchange_name: str, exchange_type: str, coin_name: str):
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.coin_name = coin_name

    @logger.catch()
    def open_position(self, parameters: str | tuple) -> str | dict:
        match self.exchange_name, self.exchange_type:
            case 'BINANCE', 'FUTURES':
                return self._open_position_futures_binance(parameters)
            case 'BINANCE', 'SPOT':
                return self._open_position_spot_binance(parameters)
            case 'BYBIT', 'FUTURES':
                return self._open_position_futures_bybit(parameters)
            case 'BYBIT', 'SPOT':
                return self._open_position_spot_bybit(parameters)
            case _:
                return ""

    @logger.catch()
    def close_position(self, position_side: str, quantity: float) -> dict | str:
        match self.exchange_name, self.exchange_type:
            case 'BINANCE', 'FUTURES':
                return self._close_position_futures_binance(self.coin_name, position_side, quantity)
            case 'BINANCE', 'SPOT':
                return self._close_position_spot_binance(self.coin_name, position_side, quantity)
            case 'BYBIT', 'FUTURES':
                return self._close_position_futures_bybit(self.coin_name, position_side, quantity)
            case 'BYBIT', 'SPOT':
                return self._close_position_spot_bybit(self.coin_name, position_side, quantity)
            case _:
                return ""

    @logger.catch()
    def _open_position_futures_binance(self, data: tuple) -> dict | str | None:
        side, price, volume, stop_price, take_price = data
        coin_info = self._get_exchange_info_coin_futures_binance(self.coin_name)
        if isinstance(coin_info, str) or not coin_info:
            return f"Не удалось получить данные по инструменту {self.coin_name}: {coin_info}"
        balance_client = self._get_free_balance_coin_futures_binance(coin_info["quoteAsset"])
        if isinstance(balance_client, str):
            return f"Не удалось получить баланс клиента: {balance_client}"
        ticker_price = ticker_price_um_futures(self.coin_name)
        if isinstance(ticker_price, str) or not ticker_price:
            logger.info(f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}")
            return f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}"

        if side == "Buy" and float(price) > float(ticker_price):
            return f"Цена инструмента {self.coin_name}: {ticker_price} ниже цены открытия {side}: {price}"
        if side == "Sell" and float(price) < float(ticker_price):
            return f"Цена инструмента {self.coin_name}: {ticker_price} выше цены открытия {side}: {price}"

        if float(coin_info["filters"][1].get("minQty")) <= float(volume):
            order = Order(self.exchange_name, self.exchange_type, self.coin_name)
            open_order = order.new_order(side=side, quantity=volume, price=ticker_price, stop=stop_price)
            return open_order
        else:
            logger.info("Недостаточно баланса для совершения операции.")
            return "Недостаточно баланса для совершения операции. " \
                   "Увеличьте используемый процент от депозита или пополните депозит."

    def _open_position_spot_binance(self, data, percentage_deposit):
        pass

    @logger.catch()
    def _open_position_futures_bybit(self, data: tuple[str, str, str, str, str]) -> tuple[dict | str, str]:
        side, price, volume, stop_price, take_price = data
        coin_info = get_instrument_info_bybit('linear', self.coin_name)
        ticker_price = get_tickers_bybit('linear', self.coin_name)['result']['list'][0]['lastPrice']

        if side == "Buy" and float(price) > float(ticker_price):
            return f"Цена инструмента {self.coin_name}: {ticker_price} ниже цены открытия {side}: {price}"
        if side == "Sell" and float(price) < float(ticker_price):
            return f"Цена инструмента {self.coin_name}: {ticker_price} выше цены открытия {side}: {price}"

        if float(coin_info["result"]['list'][0]['lotSizeFilter']['minOrderQty']) <= float(volume):
            order = Order(self.exchange_name, self.exchange_type, self.coin_name)
            open_order = order.new_order(side=side, qty=volume, price=price, take_profit=take_price,
                                         stop_loss=stop_price)
            return open_order
        else:
            logger.info("Недостаточно баланса для совершения операции.")
            return "Недостаточно баланса для совершения операции. " \
                   "Увеличьте используемый процент от депозита или пополните депозит."

    @logger.catch()
    def _open_position_spot_bybit(self, data):
        pass

    @logger.catch()
    def _close_position_futures_binance(self, position_side: str, quantity: float) -> dict | str:
        pass
        # price = 0
        # side = ''
        # ticker_price = ticker_price_um_futures(self.coin_name)
        # if isinstance(ticker_price, str):
        #     logger.info(f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}")
        #     return f"Не удалось получить цену инструмента {self.coin_name}: {ticker_price}"
        # exchange_info = self._get_exchange_info_coin_futures_binance(self.coin_name)
        # if isinstance(exchange_info, str):
        #     return f"Не удалось получить данные по инструменту {self.coin_name}: {exchange_info}"
        # if position_side == "SHORT":
        #     side = "BUY"
        #     price = float(ticker_price['price']) * 0.9998
        # elif position_side == "LONG":
        #     side = "SELL"
        #     price = float(ticker_price['price']) * 1.0002
        # rounding_accuracy = get_rounding_accuracy(exchange_info["filters"][0].get("tickSize"))
        # price_round = round(price, rounding_accuracy)
        # return Order(self.exchange_name, self.exchange_type, self.coin_name).new_order(
        #     symbol=self.coin_name,
        #     side=side,
        #     position_side=position_side,
        #     type_position="LIMIT",
        #     quantity=quantity,
        #     time_in_force="GTC",
        #     price=price_round
        # )

    @logger.catch()
    def _close_position_spot_binance(self, name_coin, position_side, quantity):
        pass

    @logger.catch()
    def _close_position_futures_bybit(self, name_coin, position_side, quantity):
        pass

    @logger.catch()
    def _close_position_spot_bybit(self, name_coin, position_side, quantity):
        pass


if __name__ == '__main__':
    logger.info('Running position.py from module exchanges/trading')
