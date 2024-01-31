import sqlite3
from loguru import logger


@logger.catch()
def connect_database():
    """Создание базы данных"""

    return sqlite3.connect('database/database.db', check_same_thread=False)


@logger.catch()
def create_database(name_tabl: str):
    connect = connect_database()
    cursor = connect.cursor()
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {name_tabl} (
                        date_time TEXT,
                        user_name TEXT,
                        exchange TEXT,
                        exchange_type TEXT,
                        strategy TEXT,
                        period TEXT,
                        signal TEXT CHECK (typeof(signal) IN ('dict', 'str', 'list')),
                        position TEXT CHECK (typeof(position) IN ('dict', 'str', 'list'))
                        )""")
    connect.commit()
    cursor.close()
    connect.close()


@logger.catch()
def db_write(date_time: str, user_name: str, exchange: str, exchange_type: str, strategy: str, ticker: str, period: str,
             signal: dict | str | list, position: dict | str | list):
    connect = connect_database()
    cursor = connect.cursor()
    cursor.execute(
        f'INSERT INTO {ticker} '
        '('
        'date_time,'
        'user_name,'
        'exchange,'
        'exchange_type,'
        'strategy,'
        'period,'
        'signal,'
        'position'
        ')'
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (date_time, user_name, exchange, exchange_type, strategy, period, signal, position)
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
