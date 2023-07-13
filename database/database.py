import datetime
import sqlite3
from loguru import logger


@logger.catch()
def connect_database():
    """Создание базы данных"""

    return sqlite3.connect('database/database.db', check_same_thread=False)


@logger.catch()
def create_database(name_tabl: str):
    """Подключение и создание таблицы"""

    connect = connect_database()
    cursor = connect.cursor()
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {name_tabl} (
                        date_time TEXT,
                        user_name TEXT,
                        exchange TEXT,
                        period TEXT,
                        EMA INTEGER,
                        MA INTEGER,
                        signal TEXT,
                        position TEXT
                        )""")
    connect.commit()
    cursor.close()
    connect.close()


@logger.catch()
def db_write(date_time: str, user_name: str, exchange: str, ticker: str, period: str, ema: int, ma: int,
             signal: str, position: str):
    """Внесение данных в базу.

    :param position:
    :param signal:
    :param ma:
    :param ema:
    :param period:
    :param ticker:
    :param exchange:
    :param user_name:
    :param date_time:
    """

    connect = connect_database()
    cursor = connect.cursor()
    cursor.execute(
        f'INSERT INTO {ticker} '
        '('
        'date_time, '
        'user_name, '
        'exchange, '
        'period, '
        'EMA, '
        'MA, '
        'signal,'
        'position'
        ') '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (date_time, user_name, exchange, period, ema, ma, signal, position)
    )
    connect.commit()
    connect.close()


@logger.catch()
async def db_read(name_tabl: str):
    connect = connect_database()
    cursor = connect.cursor()
    return cursor.execute(f'SELECT * FROM {name_tabl}').fetchall()


if __name__ == '__main__':
    logger.info('Running database.py from module database')
