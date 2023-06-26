import pandas_ta as ta
import pandas as pd

from loguru import logger


@logger.catch()
def add_moving_average(data: pd.DataFrame, period: int):
    data[f'MA_{period}'] = round(data['Close'].rolling(window=period).mean(), 2)
    return data


@logger.catch()
def add_exponential_moving_average(data: pd.DataFrame, period: int) -> pd.DataFrame:
    data[f"EMA_{period}"] = round(data['Close'].ewm(span=period, adjust=False).mean(), 2)
    return data


@logger.catch()
def add_average_true_range_period(data, period):
    data[f'ATR_{period}'] = round(ta.atr(high=data['High'], low=data['Low'], close=data['Close'], length=period), 2)
    return data


@logger.catch()
def add_MACD(data: pd.DataFrame, fast: int, slow: int, signal: int):
    macd = ta.macd(data['Close'], fast=fast, slow=slow, signal=signal)
    data['MACD'] = round(macd[f'MACD_{fast}_{slow}_{signal}'], 2)
    data['MACD_signal'] = round(macd[f'MACDs_{fast}_{slow}_{signal}'], 2)
    return data


@logger.catch()
def add_stochastic(data: pd.DataFrame, fast: int, slow: int, smooth_k=1):
    stoch = ta.stoch(data['High'], data['Low'], data['Close'], d=slow, k=fast, smooth_k=smooth_k)
    data['stoch_fast'] = round(stoch[f'STOCHk_{fast}_{slow}_{smooth_k}'], 2)
    data['stoch_slow'] = round(stoch[f'STOCHd_{fast}_{slow}_{smooth_k}'], 2)
    return data


if __name__ == '__main__':
    logger.info('Running add_indicators_to_dataframe.py from module binance_api')
