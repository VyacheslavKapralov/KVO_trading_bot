import pandas as pd
from loguru import logger

from exchanges.trading.position import Position


@logger.catch()
def add_fractals(data: pd.DataFrame) -> pd.DataFrame:
    data['fractal'] = None
    if data['High'].iloc[-3] > data['High'].iloc[-4] and data['High'].iloc[-3] > data['High'].iloc[-5] and \
            data['High'].iloc[-3] > data['High'].iloc[-2] and data['High'].iloc[-3] > data['High'].iloc[-1]:
        data['fractal'].ilock[-3] = 'up'
    if data['Low'].iloc[-3] < data['Low'].iloc[-4] and data['Low'].iloc[-3] < data['Low'].iloc[-5] and \
            data['Low'].iloc[-3] < data['Low'].iloc[-2] and data['Low'].iloc[-3] < data['Low'].iloc[-1]:
        data['fractal'].ilock[-3] = 'down'
    return data


@logger.catch()
def fractal_strategy(data: pd.DataFrame, percent: float, stop: float, take: float) -> str:
    if data['fractal'].iloc[-3] == 'up':
        position = Position(data['exchange'], data['exchange_type'], data['coin_name'], 'FRACTAL')
        return position.open_position(('SELL_STOP', stop, take), percent)
    elif data['fractal'].iloc[-3] == 'down':
        position = Position(data['exchange'], data['exchange_type'], data['coin_name'], 'FRACTAL')
        return position.open_position(('BUY_STOP', stop, take), percent)
