from loguru import logger


@logger.catch()
def log_telegram_bot():
    """Настройки логирования."""

    logger.add(
        'logs/bot_logs.log',
        rotation='1 day',
        retention='7 days',
        encoding='utf-8',
        level='DEBUG',
        format='<green>{time}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{'
               'function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> '
    )


if __name__ == '__main__':
    logger.info("Запуск start_log.py")
