import requests
from loguru import logger


@logger.catch()
def get_klines_spot_without_api(symbol: str, timeframe: str, interval: int):
    time_frame_tuple = ('1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M')
    if timeframe in time_frame_tuple:
        url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&limit={interval + 2}'
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            return f'Ошибка {response.status_code}.'


if __name__ == '__main__':
    logger.info('Запущен klines_spot_without_api.py в модуле binance_api')