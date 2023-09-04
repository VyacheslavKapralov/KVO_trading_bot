from loguru import logger
import pandas as pd

from binance_api.exchange_data.add_dataframe import get_dataframe_pandas, add_dataframe
from binance_api.get_exchange_client_info import Client
from indicators.add_indicators_to_dataframe import fibonacci_retracement_down, fibonacci_retracement_up, \
    fibonacci_expansion_up, fibonacci_expansion_down


@logger.catch()
def output_signals_fibo(exchange_type: str, symbol: str, time_frame: str, received_order: dict) -> \
        str | tuple[float, float, float] | None:
    client = Client(symbol, exchange_type)
    existing_positions = client.get_positions()
    if isinstance(existing_positions, str):
        logger.info(f"Не удалось получить информацию по открытым позициям на бирже: {existing_positions}")
        return f"Не удалось получить информацию по открытым позициям на бирже: {existing_positions}"
    elif existing_positions:
        logger.info(f"На инструменте {symbol} секции {exchange_type} есть открытые позиции: {existing_positions}")
        return f"На инструменте {symbol} секции {exchange_type} есть открытые позиции: {existing_positions}.\n" \
               f"Необходимо закрыть все имеющиеся позиции для корректной работы бота."
    data = add_dataframe(exchange_type, symbol, time_frame, limit=1)
    if isinstance(data, str):
        return data
    data = adding_dataframe_fibo(data)
    logger.info(
        f"{received_order['position']} price = {data['Close'].iloc[-1]}, "
        f"open_order: {data['fibo_0.5'].iloc[-1]}, take_profit: {data['fibo_0.236'].iloc[-1]}, "
        f"stop_loss: {data['fibo_0.618'].iloc[-1]}")
    if not received_order:
        received_order['position'] = {'open_order': data['fibo_0.5'].iloc[-1],
                                      'take_profit': data['fibo_0.236'].iloc[-1],
                                      'stop_loss': data['fibo_0.618'].iloc[-1]}
        return float(data['fibo_0.5'].iloc[-1]), float(data['fibo_0.236'].iloc[-1]), float(data['fibo_0.618'].iloc[-1])


@logger.catch()
def adding_dataframe_fibo(data: list) -> pd.DataFrame:
    data = get_dataframe_pandas(data)
    if float(data['High'].ilock[-1]) > float(data['Low'].ilock[-1]):
        data = fibonacci_retracement_down(data)
        data = fibonacci_expansion_up(data)
    else:
        data = fibonacci_retracement_up(data)
        data = fibonacci_expansion_down(data)
    return data


if __name__ == '__main__':
    logger.info('Running search_signal_fibo.py from module telegram_api.interaction_exchange')
