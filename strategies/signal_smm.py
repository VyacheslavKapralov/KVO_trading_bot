import pandas as pd
import mplfinance as mpf
from loguru import logger

from exchanges.binance_api.exchange_data.add_dataframe import get_dataframe_pandas_binance
from exchanges.binance_api.exchange_data.klines_without_apikey import get_klines_futures_without_api
from plotting.creating_graph import building_price_chart


@logger.catch()
def mark_swings(data: pd.DataFrame) -> pd.DataFrame:
    data['Swing_high'], data['Swing_low'] = 0, 0
    for num in range(1, len(data)):
        if data['High'].iloc[num] > data['High'].iloc[num - 1]:
            data['Swing_high'].iloc[num] = data['High'].iloc[num].copy()
            data['Swing_high'].iloc[num - 1] = 0
        elif data['Low'].iloc[num] < data['Low'].iloc[num - 1]:
            data['Swing_low'].iloc[num] = data['Low'].iloc[num].copy()
            data['Swing_low'].iloc[num - 1] = 0
        logger.info(f"{num}, {data['Swing_high'].iloc[num]}, {data['Swing_low'].iloc[num]}")
    return data


@logger.catch()
def search_previous_swing(data: pd.DataFrame, length_range: int, direction: str) -> int | None:
    for num in range(1, length_range):
        if direction == 'high' and data.loc[num, 'Swing_high']:
            return num
        if direction == 'low' and data.loc[num, 'Swing_low']:
            return num


@logger.catch()
def search_swings(data: pd.DataFrame):
    last_swing_high = data[data['Swing_high'] == True].tail(1)
    last_swing_low = data[data['Swing_low'] == True].tail(1)
    return last_swing_high, last_swing_low


@logger.catch()
def search_tend(data: pd.DataFrame) -> str:
    if data[data['Swing_high'] == True].tail(2)[-1] > data[data['Swing_high'] == True].tail(2)[-2]\
            and data[data['Swing_low'] == True].tail(1)[-1] > data[data['Swing_low'] == True].tail(1)[-2]:
        return 'long'
    elif data[data['Swing_high'] == True].tail(2)[-1] < data[data['Swing_high'] == True].tail(2)[-2]\
            and data[data['Swing_low'] == True].tail(1)[-1] < data[data['Swing_low'] == True].tail(1)[-2]:
        return 'short'
    return 'range'


if __name__ == '__main__':
    logger.info('Running signal_smm.py from module strategies')
    data_frame = get_klines_futures_without_api(symbol='BTCUSDT', time_frame='1h', limit=30)
    data_frame = get_dataframe_pandas_binance(data_frame)
    data_frame = mark_swings(data_frame)
    data_frame.to_csv('data_swings.csv', index=False)
    addplot=[]
    addplot.append(mpf.make_addplot(data_frame["Swing_high"], type='scatter', color='#7F7F7F', panel=0))
    addplot.append(mpf.make_addplot(data_frame['Swing_low'], type='scatter', color='#AA13E5', panel=0))
    building_price_chart(data_frame, 'BTCUSDT', '1h', addplot=addplot)



