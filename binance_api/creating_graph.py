import mplfinance as mpf
from loguru import logger
import pandas as pd


@logger.catch()
def building_price_chart(data: pd.DataFrame, coin: str, time_frame: str, addplot: list):
    return mpf.plot(
        data,
        type='candle',
        addplot=addplot,  # добавление на график объектов
        volume=True,
        datetime_format='%Y-%m-%d',
        style='binance',
        title=f'{coin} {time_frame} Candlestick Chart',
        ylabel='Price',
        figscale=1.5,
        figratio=[15.0, 8.0],
        scale_padding=dict(left=0.3, right=0.6, top=0.3, bottom=0.6)
    )


@logger.catch()
def add_price_chart_line_indicator(data: pd.DataFrame, indicators: dict, addplot: list):
    colors = (
        '#7F7F7F',
        '#E03817',
        '#E0A913',
        '#D5E012',
        '#7EE013',
        '#14E086',
        '#14DBE6',
        '#1378E5',
        '#2716E5',
        '#AA13E5',
        '#E514C8'
    )

    count = 1
    for key, val in indicators.items():
        if count > 10:
            break

        addplot.append(mpf.make_addplot(data[f"{key}_{val}"], type='line', color=colors[1], panel=0))
        count += 2

    return addplot


if __name__ == '__main__':
    logger.info('Запущен creating_graph.py из модуля binance_api')
