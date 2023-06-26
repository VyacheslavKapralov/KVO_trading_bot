import os

from dotenv import load_dotenv
from pydantic import BaseSettings, SecretStr, StrictStr

load_dotenv()


class BinanceSettings(BaseSettings):
    api_key: SecretStr = os.getenv('API_KEY', None)
    secret_key: SecretStr = os.getenv('SECRET_KEY', None)


class BotSettings(BaseSettings):
    telebot_api: SecretStr = os.getenv('TELEGRAM_TOKEN', None)
