from loguru import logger
import pandas as pd

from binance_api.exchange_data.add_dataframe import get_dataframe_pandas, add_dataframe
from indicators.add_indicators_to_dataframe import add_exponential_moving_average, add_moving_average


@logger.catch()
def adding_dataframe_ema(data: list, period_stop: int, period_fast: int, period_slow: int) -> pd.DataFrame:
    data = get_dataframe_pandas(data)
    data = add_exponential_moving_average(data, period=period_stop)
    data = add_exponential_moving_average(data, period=period_fast)
    data = add_moving_average(data, period=period_slow)
    return data


@logger.catch()
def add_position(data: pd.DataFrame, period_stop: int, period_fast: int, period_slow: int) -> str | None:
    if data[f'EMA_{period_stop}'].iloc[-1] * 0.998 < data[f'MA_{period_slow}'].iloc[-1] < \
            data[f'EMA_{period_stop}'].iloc[-1] * 1.002:
        return

    elif data[f'EMA_{period_fast}'].iloc[-1] > data[f'MA_{period_slow}'].iloc[-1] and \
            data[f'EMA_{period_stop}'].iloc[-1] < data['Open'].iloc[-1]:
        return 'LONG'
    elif data[f'EMA_{period_fast}'].iloc[-1] < data[f'MA_{period_slow}'].iloc[-1] and \
            data[f'EMA_{period_stop}'].iloc[-1] < data['Open'].iloc[-1]:
        return 'CLOSE_LONG'
    elif data[f'EMA_{period_fast}'].iloc[-1] < data[f'MA_{period_slow}'].iloc[-1] and \
            data[f'EMA_{period_stop}'].iloc[-1] > data['Open'].iloc[-1]:
        return 'SHORT'
    elif data[f'EMA_{period_fast}'].iloc[-1] > data[f'MA_{period_slow}'].iloc[-1] and \
            data[f'EMA_{period_stop}'].iloc[-1] > data['Open'].iloc[-1]:
        return 'CLOSE_SHORT'
    elif data[f'EMA_{period_stop}'].iloc[-1] < data['Open'].iloc[-1]:
        return 'LONG'
    elif data[f'EMA_{period_stop}'].iloc[-1] > data['Open'].iloc[-1]:
        return 'SHORT'


@logger.catch()
def output_signals_ema(exchange_type: str, symbol: str, time_frame: str, period_stop: int, period_fast: int,
                       period_slow: int, current_position_last: dict) -> tuple[bool, str] | None:
    data = add_dataframe(exchange_type, symbol, time_frame, period_stop)
    if isinstance(data, str):
        return False, data
    data = adding_dataframe_ema(data, period_stop, period_fast, period_slow)
    current_position = add_position(data, period_stop, period_fast, period_slow)
    logger.info(
        f"{current_position_last['position']}/{current_position} price = {data['Open'].iloc[-1]}, "
        f"Stop_EMA: {data[f'EMA_{period_stop}'].iloc[-1]}, EMA: {data[f'EMA_{period_fast}'].iloc[-1]}, "
        f"MA: {data[f'MA_{period_slow}'].iloc[-1]}")
    if not current_position_last['position'] and current_position == "LONG" or current_position == "SHORT":
        current_position_last['position'] = current_position
        return True, current_position
    if current_position_last['position'] == current_position:
        return
    current_position_last['position'] = current_position
    return True, current_position


if __name__ == '__main__':
    logger.info('Running search_signal_ema.py from module telegram_api.interaction_exchange')
