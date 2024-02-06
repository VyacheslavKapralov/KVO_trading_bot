from loguru import logger

from utils.add_dataframe import adding_dataframe_ema, add_data_frame


@logger.catch()
def add_position(data, period_stop: int, period_fast: int, period_slow: int) -> str | None:
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
async def output_signals_ema(current_position_last: dict, settings: dict) -> tuple[bool, str | None]:
    data = add_data_frame(settings)
    if isinstance(data, str):
        return False, data

    period_stop, period_fast, period_slow = settings['stop_line'], settings['ema'], settings['ma']
    data = adding_dataframe_ema(data, period_stop, period_fast, period_slow)
    current_position = add_position(data, period_stop, period_fast, period_slow)
    logger.info(
        f"Previous position: {current_position_last['position']}/ "
        f"Current position: {current_position} price: {data['Open'].iloc[-1]}, "
        f"Stop_EMA: {data[f'EMA_{period_stop}'].iloc[-1]}, EMA: {data[f'EMA_{period_fast}'].iloc[-1]}, "
        f"MA: {data[f'MA_{period_slow}'].iloc[-1]}")
    if current_position_last['position'] != current_position:
        current_position_last['position'] = current_position
        return True, current_position
    return False, None


if __name__ == '__main__':
    logger.info('Running search_signal_ema.py from module strategies')
