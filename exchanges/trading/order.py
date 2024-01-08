# import time
#
# from loguru import logger
# from binance.error import ClientError
# from exchanges.binance_api.connect_binance import connect_um_futures_client, connect_spot_client
# from exchanges.trading.position import Position
#
#
# class Order(Position):
#
#     @logger.catch()
#     def new_order(self, *args):
#         if self.exchange_name == 'BINANCE':
#             if self.exchange_type == 'FUTURES':
#                 return self._new_order_um_futures_binance(self, args)
#             elif self.exchange_type == 'SPOT':
#                 return self._new_order_spot_binance()
#         elif self.exchange_name == 'BYBIT':
#             if self.exchange_type == 'FUTURES':
#                 pass
#             elif self.exchange_type == 'SPOT':
#                 pass
#         else:
#             return ""
#
#     @logger.catch()
#     def get_all_orders(self):
#         if self.exchange_name == 'BINANCE':
#             if self.exchange_type == 'FUTURES':
#                 return self._get_all_orders_um_futures_binance()
#             elif self.exchange_type == 'SPOT':
#                 return self._get_all_orders_spot_binance()
#         elif self.exchange_name == 'BYBIT':
#             if self.exchange_type == 'FUTURES':
#                 pass
#             elif self.exchange_type == 'SPOT':
#                 pass
#         else:
#             return ""
#
#     @logger.catch()
#     def get_orders(self):
#         if self.exchange_name == 'BINANCE':
#             if self.exchange_type == 'FUTURES':
#                 return self._get_orders_um_futures_binance()
#             elif self.exchange_type == 'SPOT':
#                 return self._get_orders_spot()
#         elif self.exchange_name == 'BYBIT':
#             if self.exchange_type == 'FUTURES':
#                 pass
#             elif self.exchange_type == 'SPOT':
#                 pass
#         else:
#             return ""
#
#     def cancel_all_open_orders(self):
#         if self.exchange_name == 'BINANCE':
#             if self.exchange_type == 'FUTURES':
#                 return self._cancel_all_open_orders_um_futures_binance()
#             elif self.exchange_type == 'SPOT':
#                 return self._cancel_all_open_orders_spot_binance()
#         elif self.exchange_name == 'BYBIT':
#             if self.exchange_type == 'FUTURES':
#                 pass
#             elif self.exchange_type == 'SPOT':
#                 pass
#         else:
#             return ""
#
#     @logger.catch()
#     def cancel_open_orders(self):
#         if self.exchange_name == 'BINANCE':
#             if self.exchange_type == 'FUTURES':
#                 return self._cancel_open_order_um_futures_binance()
#             elif self.exchange_type == 'SPOT':
#                 return self._cancel_open_order_spot_binance()
#         elif self.exchange_name == 'BYBIT':
#             if self.exchange_type == 'FUTURES':
#                 pass
#             elif self.exchange_type == 'SPOT':
#                 pass
#         else:
#             return ""
#
#     @logger.catch()
#     def _new_order_um_futures_binance(self, side: str, position_side: str, type_position: str, quantity: float,
#                                       time_in_force: str, price: float = None, stop: float = None) -> dict | str:
#         count = 0
#         while True:
#             try:
#                 return connect_um_futures_client().new_order(
#                     symbol=self.coin_name,
#                     side=side,
#                     positionSide=position_side,
#                     type=type_position,
#                     quantity=quantity,
#                     timeInForce=time_in_force,
#                     price=price,
#                     stopPrice=stop
#                 )
#             except ClientError as error:
#                 logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
#                             f"error message: {error.error_message}")
#                 return error.error_message
#             except Exception as e:
#                 logger.info(f"Не удается создать ордер. Ошибка: {e}")
#                 if count == 3:
#                     return f"Не удалось создать ордер. Ошибка: {e}"
#                 count += 1
#                 time.sleep(2)
#
#     @logger.catch()
#     def _new_order_spot_binance(self, side: str, type_position: str, quantity: float, time_in_force: str,
#                                 price: float) -> dict | str:
#         count = 0
#         while True:
#             try:
#                 return connect_spot_client().new_order(
#                     symbol=self.coin_name,
#                     side=side,
#                     type=type_position,
#                     quantity=quantity,
#                     timeInForce=time_in_force,
#                     price=price
#                 )
#             except ClientError as error:
#                 logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
#                             f"error message: {error.error_message}")
#                 return error.error_message
#             except Exception as e:
#                 logger.info(f"Не удается создать ордер. Ошибка: {e}")
#                 if count == 3:
#                     return f"Не удалось создать ордер. Ошибка: {e}"
#                 count += 1
#                 time.sleep(2)
#
#     @logger.catch()
#     def _cancel_all_open_orders_um_futures_binance(self) -> dict | str:
#         try:
#             return connect_um_futures_client().cancel_open_orders(symbol=self.coin_name, recvWindow=6000)
#         except ClientError as error:
#             logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
#                         f"error message: {error.error_message}")
#             return error.error_message
#
#     @logger.catch()
#     def _cancel_open_order_um_futures_binance(self, order_id: int) -> dict | str:
#         try:
#             return connect_um_futures_client().cancel_order(symbol=self.coin_name, orderId=order_id, recvWindow=6000)
#         except ClientError as error:
#             logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
#                         f"error message: {error.error_message}")
#             return error.error_message
#
#     @logger.catch()
#     def _cancel_all_open_orders_spot_binance(self) -> dict | str:
#         try:
#             return connect_spot_client().cancel_open_orders(symbol=self.coin_name, recvWindow=6000)
#         except ClientError as error:
#             logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
#                         f"error message: {error.error_message}")
#             return error.error_message
#
#     @logger.catch()
#     def _cancel_open_order_spot_binance(self, order_id: str) -> dict | str:
#         try:
#             return connect_spot_client().cancel_order(symbol=self.coin_name, orderId=order_id, recvWindow=6000)
#         except ClientError as error:
#             logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
#                         f"error message: {error.error_message}")
#             return error.error_message
#
#     @logger.catch()
#     def _get_all_orders_um_futures_binance(self) -> dict | str:
#         try:
#             return connect_um_futures_client().get_all_orders(symbol=self.coin_name, recvWindow=6000)
#         except ClientError as error:
#             logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
#                         f"error message: {error.error_message}")
#             return error.error_message
#
#     @logger.catch()
#     def _get_all_orders_spot_binance(self) -> dict | str:
#         try:
#             return connect_spot_client().get_orders(symbol=self.coin_name, recvWindow=6000)
#         except ClientError as error:
#             logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
#                         f"error message: {error.error_message}")
#             return error.error_message
#
#     @logger.catch()
#     def _get_orders_um_futures_binance(self) -> dict | str:
#         try:
#             return connect_um_futures_client().get_orders(symbol=self.coin_name, recvWindow=6000)
#         except ClientError as error:
#             logger.info(f"Found error status: {error.status_code}, error code: {error.error_code}, "
#                         f"error message: {error.error_message}")
#             return error.error_message
#
#
# if __name__ == '__main__':
#     logger.info('Running order.py from module exchanges/trading')
