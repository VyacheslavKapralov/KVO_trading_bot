import os

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseSettings, SecretStr

load_dotenv()


class BinanceSettings(BaseSettings):
    api_key: SecretStr = os.getenv('BINANCE_API_KEY', None)
    secret_key: SecretStr = os.getenv('BINANCE_SECRET_KEY', None)


class BybitSettings(BaseSettings):
    api_key: SecretStr = os.getenv('BYBIT_API_KEY', None)
    secret_key: SecretStr = os.getenv('BYBIT_SECRET_KEY', None)


class BotSettings(BaseSettings):
    telebot_api: SecretStr = os.getenv('TELEGRAM_TOKEN', None)


if __name__ == '__main__':
    logger.info('Running settings.py')
