import datetime
from loguru import logger


@logger.catch()
def get_timeout_response(time_frame: str) -> int:
    time_frame_dict = {'1m': 60, '3m': 180, '5m': 300, '15m': 900, '30m': 1800, '1h': 3600, '2h': 7200, '4h': 14400,
                       '6h': 21600, '8h': 28800, '12h': 43200, '1d': 86400, '3d': 259200, '1w': 604800, '1M': 2592000}

    return time_frame_dict.get(time_frame)


@logger.catch()
def get_waiting_time(now, time_frame: str) -> int:

    number_period = int(time_frame[:-1])

    if time_frame.endswith('m'):
        start_minute = int(now.minute) // number_period * number_period
        start_time = now.replace(minute=start_minute, second=0, microsecond=0)
        end_time = start_time + datetime.timedelta(minutes=number_period)
    elif time_frame.endswith('h'):
        start_hour = now.hour // number_period * number_period
        start_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_time = start_time + datetime.timedelta(hours=number_period)
    elif time_frame.endswith('d'):
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + datetime.timedelta(days=number_period)

    elif time_frame.endswith('w'):
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + datetime.timedelta(weeks=number_period)

    return round((end_time - now).total_seconds())


if __name__ == '__main__':
    logger.info('Running time_frames_editing.py from module telegram_api.interaction_exchange')
