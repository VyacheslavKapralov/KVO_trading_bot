import pandas as pd
from loguru import logger


@logger.catch()
def get_dataframe_pandas(data: list) -> pd.DataFrame:
    data_frame = pd.DataFrame(
        data,
        columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_asset_volume',
                 'Number_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume',
                 'Ignore']
    )
    data_frame = data_frame.drop(
        columns=['Close_time', 'Quote_asset_volume', 'Number_of_trades', 'Taker_buy_base_asset_volume',
                 'Taker_buy_quote_asset_volume', 'Ignore']
    )
    data_frame['Date'] = pd.to_datetime(data_frame['Date'], unit='ms')
    data_frame = data_frame.set_index('Date')
    data_frame[['Open', 'High', 'Low', 'Close', 'Volume']] = \
        data_frame[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
    return data_frame


if __name__ == '__main__':
    logger.info('Running add_dataframe_pandas.py from module binance_api')
