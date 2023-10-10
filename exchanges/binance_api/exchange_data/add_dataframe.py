import pandas as pd
from loguru import logger
from exchanges.binance_api.exchange_data.klines_without_apikey import get_klines_futures_without_api, \
    get_klines_spot_without_api
from indicators.add_indicators_to_dataframe import add_exponential_moving_average, add_moving_average


@logger.catch()
def add_dataframe(exchange_type: str, symbol: str, time_frame: str, limit: int) -> list | str:
    if exchange_type == 'SPOT':
        return get_klines_spot_without_api(symbol, time_frame, limit)
    elif exchange_type == 'FUTURES':
        return get_klines_futures_without_api(symbol, time_frame, limit)


@logger.catch()
def get_dataframe_pandas(data: list) -> pd.DataFrame:
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
    # data_frame = data_frame.set_index('Date')
    data_frame[['Open', 'High', 'Low', 'Close', 'Volume']] = \
        data_frame[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
    return data_frame


@logger.catch()
def adding_dataframe_ema(data: list, period_stop: int, period_fast: int, period_slow: int) -> pd.DataFrame:
    data = get_dataframe_pandas(data)
    data = add_exponential_moving_average(data, period=period_stop)
    data = add_exponential_moving_average(data, period=period_fast)
    data = add_moving_average(data, period=period_slow)
    return data


if __name__ == '__main__':
    logger.info('Running add_dataframe.py from module binance_api')
