import requests
import time
from loguru import logger


@logger.catch()
def get_klines_futures_without_api(symbol: str, timeframe: str, limit: int):
    time_frame_tuple = ('1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M')
    if timeframe in time_frame_tuple:
        while True:
            try:
                url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={timeframe}&limit={limit + 2}'
                response = requests.get(url, timeout=5)

                if response.status_code == 200:
                    return response.json()
                else:
                    return f'Ошибка {response.status_code}'
            except Exception as e:
                logger.info(f"Не удается получить данные от сервера. Ошибка: {e}")
                time.sleep(2)


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
    logger.info('Running klines_without_apikey.py from module binance_api')
    print(get_klines_futures_without_api(symbol="LTCUSDT", timeframe="1m", limit=100))
