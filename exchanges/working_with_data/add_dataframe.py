import pandas as pd
from loguru import logger

from exchanges.binance_api.klines_without_apikey import get_klines_futures_without_api, get_klines_spot_without_api
from exchanges.bybit_api.coin_info import get_kline_bybit
from exchanges.working_with_data.time_frames_editing import get_interval_for_bybit
from indicators.add_indicators_to_dataframe import add_exponential_moving_average, add_moving_average


@logger.catch()
def add_data_frame(strategy_settings):
    match strategy_settings['exchange'], strategy_settings['exchange_type']:
        case 'BYBIT', 'FUTURES':
            klines = get_kline_bybit('linear', strategy_settings['coin_name'],
                                     get_interval_for_bybit(strategy_settings['time_frame']))
            return get_dataframe_pandas_bybit(klines['result']['list'])
        case 'BYBIT', 'SPOT':
            klines = get_kline_bybit('spot', strategy_settings['coin_name'],
                                     get_interval_for_bybit(strategy_settings['time_frame']))
        case 'BINANCE', 'FUTURES':
            klines = get_klines_futures_without_api(strategy_settings['coin_name'], strategy_settings['time_frame'])
            return get_dataframe_pandas_binance(klines)
        case 'BINANCE', 'SPOT':
            klines = get_klines_spot_without_api(strategy_settings['coin_name'], strategy_settings['time_frame'])


@logger.catch()
def get_dataframe_pandas_binance(data: list) -> pd.DataFrame:
    data_frame = pd.DataFrame(
        data,
        columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_asset_volume',
                 'Number_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume',
                 'Ignore']
    )
    data_frame = data_frame.drop(
        columns=['Close_time', 'Quote_asset_volume', 'Number_of_trades', 'Taker_buy_base_asset_volume',
                 'Taker_buy_quote_asset_volume', 'Ignore']
    )
    data_frame['Date'] = pd.to_datetime(data_frame['Date'], unit='ms')
    data_frame = data_frame.set_index('Date')
    data_frame[['Open', 'High', 'Low', 'Close', 'Volume']] = \
        data_frame[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
    return data_frame


@logger.catch()
def get_dataframe_pandas_bybit(data: list) -> pd.DataFrame:
    data_frame = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover'])
    data_frame = data_frame.drop(columns=['Turnover'])
    data_frame['Date'] = pd.to_datetime(data_frame['Date'], unit='ms')
    data_frame = data_frame.reindex(index=data_frame.index[::-1])
    data_frame.reset_index(inplace=True)
    data_frame.drop(columns='index', inplace=True)
    data_frame[['Open', 'High', 'Low', 'Close', 'Volume']] = \
        data_frame[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
    return data_frame


@logger.catch()
def adding_dataframe_ema(data: pd.DataFrame, period_stop: int, period_fast: int, period_slow: int) -> pd.DataFrame:
    data = add_exponential_moving_average(data, period=period_stop)
    data = add_exponential_moving_average(data, period=period_fast)
    data = add_moving_average(data, period=period_slow)
    return data


if __name__ == '__main__':
    logger.info('Running add_dataframe.py from module binance_api')
