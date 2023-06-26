import sqlite3
from loguru import logger


@logger.catch()
def connect_database():
    """Создание базы данных"""

    return sqlite3.connect('database/database.db', check_same_thread=False)


@logger.catch()
def create_database():
    """Подключение и создание таблицы"""

    connect = connect_database()
    # Создание таблицы
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS binance_signal (
                        date_time TEXT,
                        client_id INTEGER, 
                        user_name TEXT,
                        exchange TEXT,
                        ticker TEXT,
                        period TEXT,
                        EMA INTEGER,
                        MA INTEGER,
                        signal TEXT
                        )""")
    # Сохранение изменений
    connect.commit()
    cursor.close()
    # Закрытие подключения
    connect.close()


@logger.catch()
def db_write(date_time, client_id: int, user_name: str, exchange: str, ticker: str, period: str, ema: int, ma: int,
             signal: str):
    """Внесение данных в базу.

    :param signal:
    :param ma:
    :param ema:
    :param period:
    :param ticker:
    :param exchange:
    :param user_name:
    :param date_time:
    :param client_id: (int) ID пользователя
    """

    logger.info(f"Внесение в базу данных:\n"
                f"{date_time, client_id, user_name, exchange, ticker, period, ema, ma, signal}")

    connect = connect_database()
    cursor = connect.cursor()
    cursor.execute(
        'INSERT INTO binance_signal '
        '('
        'date_time, '
        'client_id, '
        'user_name, '
        'exchange, '
        'ticker, '
        'period, '
        'EMA, '
        'MA, '
        'signal'
        ') '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (date_time, client_id, user_name, exchange, ticker, period, ema, ma, signal)
    )
    connect.commit()
    connect.close()


@logger.catch()
async def db_read():
    connect = connect_database()
    cursor = connect.cursor()
    return cursor.execute('SELECT * FROM binance_signal').fetchall()


if __name__ == '__main__':
    logger.info('Запущен database.py из модуля database')
