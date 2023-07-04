from loguru import logger
import pandas as pd
import numpy as np

from working_with_data.add_dataframe_pandas import get_dataframe_pandas
from working_with_data.add_indicators_to_dataframe import add_exponential_moving_average, add_moving_average
from binance_api.exchange_data.klines_without_apikey import get_klines_futures_without_api, get_klines_spot_without_api


@logger.catch()
def add_dataframe(exchange_type, symbol, time_frame, period_trend_line):
    if exchange_type == 'SPOT':
        return get_klines_spot_without_api(symbol, time_frame, period_trend_line)
    elif exchange_type == 'FUTURES':
        return get_klines_futures_without_api(symbol, time_frame, period_trend_line)


@logger.catch()
def adding_dataframe_ema(data, period_fast, period_slow, period_trend_line):
    data = get_dataframe_pandas(data)
    data = add_exponential_moving_average(data, period=period_fast)
    data = add_exponential_moving_average(data, period=period_trend_line)
    data = add_moving_average(data, period=period_slow)
    return data


@logger.catch()
def add_position(data: pd.DataFrame, period_fast: int, period_slow: int):
    data['position'] = np.where(data[f'EMA_{period_fast}'] - data[f'MA_{period_slow}'] > 0, 'long', 'short')
    return data


@logger.catch()
def output_signals(exchange_type: str, symbol: str, timeframe: str, period_fast: int, period_slow: int,
                   period_trend_line: int) -> str:
    data = add_dataframe(exchange_type, symbol, timeframe, period_trend_line)
    data = adding_dataframe_ema(data, period_fast, period_slow, period_trend_line)
    data = add_position(data, period_fast, period_slow)

    if data['position'][-2] == 'long' and data['position'][-1] == 'short' \
            and data['Close'][-1] < data[f"EMA_{period_trend_line}"][-1]:
        return 'SHORT'

    elif data['position'][-2] == 'short' and data['position'][-1] == 'long' \
            and data['Close'][-1] > data[f"EMA_{period_trend_line}"][-1]:
        return 'LONG'


if __name__ == '__main__':
    logger.info('Running search_signal.py from module telegram_api.interaction_exchange')
