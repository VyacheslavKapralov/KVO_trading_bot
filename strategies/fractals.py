import pandas as pd
from loguru import logger

from exchanges.bibit_api.coin_info import get_instrument_info
from exchanges.trading.order import Order
from exchanges.trading.position import Position
from indicators.add_indicators_to_dataframe import add_average_true_range_period


@logger.catch()
def add_fractals(data: pd.DataFrame, period: int) -> pd.DataFrame:
    data['fractal'] = None
    max_high = data['High'].tail(period).max()
    max_high_index = data[data['high'] == max_high].index[-1]
    data.loc[max_high_index, 'fractal'] = 'up'
    min_low = data['Low'].tail(period).min()
    min_low_index = data[data['Low'] == min_low].index[-1]
    data.loc[min_low_index, 'fractal'] = 'down'
    return data


@logger.catch()
def find_last_two_ups(data: pd.DataFrame):
    up_rows = data[data['fractal'] == 'up']
    last_two_ups = up_rows.tail(2)
    highs = last_two_ups['high'].values
    return highs


@logger.catch()
def find_last_two_downs(data: pd.DataFrame):
    down_rows = data[data['fractal'] == 'down']
    last_two_downs = down_rows.tail(2)
    downs = last_two_downs['Low'].values
    return downs


@logger.catch()
def direction_determination(data: pd.DataFrame) -> str | tuple[str, str]:
    highs = find_last_two_ups(data)
    downs = find_last_two_downs(data)
    if highs[1] >= highs[0] and downs[1] >= downs[0]:
        return 'LONG', 'SHORT'
    elif highs[0] > highs[1] and downs[0] >= downs[1]:
        return 'LONG'
    elif highs[0] <= highs[1] and downs[0] < downs[1]:
        return 'SHORT'
    return


@logger.catch()
def fractal_strategy(data_frame: pd.DataFrame, strategy_settings: dict) -> None | dict:
    # дописать функционал открытия ордера

    sent_order = {}
    data_frame = add_fractals(data_frame, strategy_settings['period'])
    direction = direction_determination(data_frame)
    if not direction:
        return

    order = Order(strategy_settings['exchange'], strategy_settings['exchange_type'], strategy_settings['coin_name'],
                  strategy_settings['strategy'])
    if strategy_settings['stop_loss_selection'] == 'atr' or strategy_settings['take_profit_selection'] == 'atr':
        data_frame = add_average_true_range_period(data_frame, strategy_settings['period'])
        stop_loss = data_frame[f"ATR-{strategy_settings['period']}"].iloct[-1]
        take_profit = stop_loss * strategy_settings['multiplicity_atr']
    elif strategy_settings['stop_loss_selection'] == 'percent' \
            and strategy_settings['take_profit_selection'] == 'percent':
        stop_loss = stop_loss_amount_usd(strategy_settings)
        take_profit = take_profit_amount_usd(strategy_settings)
    else:
        stop_loss = strategy_settings['stop_loss']
        take_profit = strategy_settings['take_profit']

    for elem in direction:
        sent_order.update(order.new_order())
    return sent_order


@logger.catch()
def stop_loss_amount_usd(data):
    client = Position(data['exchange'], data['exchange_type'], data['coin_name'])
    balance = client.get_balance()
    ticker_data = get_instrument_info(data['exchange_type'], data['coin_name'])


@logger.catch()
def take_profit_amount_usd(data):
    client = Position(data['exchange'], data['exchange_type'], data['coin_name'])
    balance = client.get_balance()
    ticker_data = get_instrument_info(data['exchange_type'], data['coin_name'])


if __name__ == '__main__':
    logger.info('Running fractals.py from module strategies')
