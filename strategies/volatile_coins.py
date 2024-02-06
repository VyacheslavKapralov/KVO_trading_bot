from loguru import logger

from exchanges.bybit_api.coin_info import get_instrument_info_bybit
from utils.add_dataframe import add_data_frame
from utils.time_frames_editing import get_time_seconds
from utils.add_indicators_to_dataframe import add_average_true_range_period


def get_period_atr(settings: dict) -> int:
    period = get_time_seconds(settings['period'])
    time_frame = get_time_seconds(settings['time_frame'])
    return period // time_frame


def sort_dictionary(dictionary: dict, ascending: str = 'True', limit: int = 5, reverse: bool = False) -> dict:
    if ascending == 'False':
        reverse = True
    sorted_dict = dict(sorted(dictionary.items(), key=lambda x: x[1], reverse=reverse))
    if reverse:
        return dict(list(sorted_dict.items())[:limit])
    return dict(list(sorted_dict.items())[-limit:])


async def volatile_coins(settings: dict) -> dict:
    coins = [elem['symbol'] for elem in get_instrument_info_bybit()['result']['list']]
    result = {}
    for coin in range(len(coins)):
        settings['coin_name'] = coins[coin]
        period = get_period_atr(settings)
        data_frame = add_data_frame(settings, period + 1)
        data_frame = add_average_true_range_period(data_frame, period)
        data_frame = data_frame.dropna(subset=[f'ATR_{period}'])
        data_frame['ATR_percent'] = data_frame[f'ATR_{period}'] / data_frame['Close'] * 100
        result[coins[coin]] = round(data_frame[f'ATR_percent'].iloc[-1], 1)
    return sort_dictionary(result, settings['ascending'], settings['top_number'])


if __name__ == '__main__':
    logger.info('Running volatile_coins.py from module strategies')
