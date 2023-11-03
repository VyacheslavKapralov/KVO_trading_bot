import requests
import time
from loguru import logger


@logger.catch()
def get_klines_futures_without_api(symbol: str, time_frame: str, limit: int) -> list | str:
    time_frame_tuple = ('1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M')
    if time_frame in time_frame_tuple:
        count = 0
        while True:
            try:
                url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={time_frame}&limit={limit + 2}'
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                return f"Не удалось получить исторические цены от сервера. Ошибка: {e}"

            except Exception as e:
                if count == 3:
                    return f"Не удалось получить исторические цены от сервера. Ошибка: {e}"

                logger.info(f"Не удается получить исторические цены от сервера. Ошибка: {e}")
                count += 1
                time.sleep(2)


@logger.catch()
def get_klines_spot_without_api(symbol: str, timeframe: str, limit: int) -> list | str:
    time_frame_tuple = ('1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M')
    if timeframe in time_frame_tuple:
        count = 0
        while True:
            try:
                url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&limit={limit + 2}'
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                return f"Не удалось получить исторические цены от сервера. Ошибка: {e}"
            except Exception as e:
                logger.info(f"Не удается получить исторические цены от сервера. Ошибка: {e}")
                if count == 5:
                    return f"Не удалось получить исторические цены от сервера. Ошибка: {e}"
                count += 1
                time.sleep(2)


if __name__ == '__main__':
    logger.info('Running klines_without_apikey.py from module binance_api')
