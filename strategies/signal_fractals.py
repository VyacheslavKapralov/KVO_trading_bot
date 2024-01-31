import pandas as pd
from loguru import logger

from exchanges.bybit_api.coin_info import get_instrument_info_bybit, get_fee_bybit
from exchanges.client.client import Client
from exchanges.trading.position import Position
from exchanges.working_with_data.add_dataframe import add_data_frame
from indicators.add_indicators_to_dataframe import add_average_true_range_period, add_fractals_indicator


@logger.catch()
def find_last_fractals(data_frame: pd.DataFrame, name_colum: str, quantity: int) -> list[float]:
    fractal_indices = data_frame[data_frame[name_colum] == True].index.tolist()

    if len(fractal_indices) >= quantity:
        last_two_fractal_indices = fractal_indices[-quantity:]
        last_two_fractal_prices = data_frame.loc[last_two_fractal_indices, 'Fractal_Price'].tolist()
        return last_two_fractal_prices
    return None


@logger.catch()
def direction_determination(data: pd.DataFrame) -> dict:
    highs = find_last_fractals(data, 'Up_Fractal', 3)
    downs = find_last_fractals(data, 'Down_Fractal', 3)
    logger.info(f"\nhighs - {highs}\ndowns - {downs}")
    try:
        if highs[1] < highs[2] and downs[1] <= downs[2]:
            return {'Buy': downs[2]}
        elif highs[1] >= highs[2] and downs[1] > downs[2]:
            return {'Sell': highs[2]}
        elif highs[2] >= highs[1] >= highs[0] and downs[2] >= downs[1] >= downs[0]:
            return {'Buy': downs[2], 'Sell': highs[2]}
        elif highs[2] * 1.005 >= highs[0] >= highs[2] * 0.995 and downs[2] * 1.005 >= downs[0] >= downs[2] * 0.995:
            return {'Buy': downs[2], 'Sell': highs[2]}

    except IndexError:
        return {}


@logger.catch()
def signal_open_position(data: pd.DataFrame, direction: dict) -> list:
    high = data.tail(1)['High'].values[0]
    low = data.tail(1)['Low'].values[0]
    signals = []

    for side, price_indicator in direction.items():
        logger.info(f"\nhigh - {high}\nlow - {low}\nprice_indicator - {price_indicator}")

        if side == 'Sell' and high > price_indicator or side == 'Buy' and low < price_indicator:
            signals.append([side, price_indicator])
    return signals


@logger.catch()
def get_open_position_price(data: pd.DataFrame, side: str, strategy_settings: dict) -> float | None:
    logger.info(f"\nDown - {find_last_fractals(data, 'Down_Fractal', 1)[0]}"
                f"\nUp - {find_last_fractals(data, 'Up_Fractal', 1)[0]}"
                f"\nrollback - {strategy_settings['rollback']}")

    match strategy_settings['rollback'], side:
        case 'usdt', 'Buy':
            return find_last_fractals(data, 'Down_Fractal', 1)[0] - strategy_settings['rollback_num']
        case 'percent', 'Buy':
            return find_last_fractals(data, 'Down_Fractal', 1)[0] - strategy_settings['rollback_num'] / 100
        case 'atr', 'Buy':
            return find_last_fractals(data, 'Down_Fractal', 1)[0] - data[f"ATR_{strategy_settings['period']}"].iloc[-1]
        case 'None', 'Buy':
            return find_last_fractals(data, 'Down_Fractal', 1)[0]
        case 'usdt', 'Sell':
            return find_last_fractals(data, 'Up_Fractal', 1)[0] + strategy_settings['rollback_num']
        case 'percent', 'Sell':
            return find_last_fractals(data, 'Up_Fractal', 1)[0] + strategy_settings['rollback_num'] / 100
        case 'atr', 'Sell':
            return find_last_fractals(data, 'Up_Fractal', 1)[0] + data[f"ATR_{strategy_settings['period']}"].iloc[-1]
        case 'None', 'Sell':
            return find_last_fractals(data, 'Up_Fractal', 1)[0]
        case _:
            return


@logger.catch()
def calculation_stop_take_usd(balance_client: float, data_frame: pd.DataFrame, strategy_settings: dict,
                              volume: float) -> [float | None, float | None]:
    match strategy_settings['stop_loss_selection'], strategy_settings['take_profit_selection']:
        case 'atr', 'atr':
            stop_loss_usd = data_frame[f"ATR_{strategy_settings['period']}"].iloc[-1]
            take_profit_usd = stop_loss_usd * strategy_settings['multiplicity_atr']
            return stop_loss_usd, take_profit_usd
        case 'atr', 'percent':
            stop_loss_usd = data_frame[f"ATR_{strategy_settings['period']}"].iloc[-1]
            take_profit_usd = balance_client * strategy_settings['take_profit'] / 100
            return stop_loss_usd, take_profit_usd
        case 'atr', 'usdt':
            stop_loss_usd = data_frame[f"ATR_{strategy_settings['period']}"].iloc[-1]
            take_profit_usd = strategy_settings['take_profit'] / volume
            return stop_loss_usd, take_profit_usd
        case 'percent', 'percent':
            stop_loss_usd = balance_client * strategy_settings['stop_loss'] / 100
            take_profit_usd = balance_client * strategy_settings['take_profit'] / 100
            return stop_loss_usd, take_profit_usd
        case 'percent', 'atr':
            stop_loss_usd = balance_client * strategy_settings['stop_loss'] / 100
            take_profit_usd = data_frame[f"ATR_{strategy_settings['period']}"].iloc[-1] * strategy_settings[
                'multiplicity_atr']
            return stop_loss_usd, take_profit_usd
        case 'percent', 'usdt':
            stop_loss_usd = balance_client * strategy_settings['stop_loss'] / 100
            take_profit_usd = strategy_settings['take_profit'] / volume
            return stop_loss_usd, take_profit_usd
        case 'usdt', 'usdt':
            stop_loss_usd = strategy_settings['stop_loss'] / volume
            take_profit_usd = strategy_settings['take_profit'] / volume
            return stop_loss_usd, take_profit_usd
        case 'usdt', 'atr':
            stop_loss_usd = strategy_settings['stop_loss'] / volume
            take_profit_usd = data_frame[f"ATR_{strategy_settings['period']}"].iloc[-1] * strategy_settings[
                'multiplicity_atr']
            return stop_loss_usd, take_profit_usd
        case 'usdt', 'percent':
            stop_loss_usd = strategy_settings['stop_loss'] / volume
            take_profit_usd = balance_client * strategy_settings['take_profit'] / 100
            return stop_loss_usd, take_profit_usd
        case _:
            return None, None


@logger.catch()
def calculation_stop_take(side: str, open_position_price: float, stop_loss_usd: float,
                          take_profit_usd: float) -> [float, float]:
    if side == 'Buy':
        stop_loss = open_position_price - stop_loss_usd
        take_profit = open_position_price + take_profit_usd
    else:
        stop_loss = open_position_price + stop_loss_usd
        take_profit = open_position_price - take_profit_usd
    return stop_loss, take_profit


@logger.catch()
def calculation_fee(price_round: float, strategy_settings: dict, volume: float) -> str:
    fee = get_fee_bybit('linear', strategy_settings['coin_name'])['result']['list'][0]['makerFeeRate']
    logger.info(f"fee - {fee}")

    if isinstance(fee, str):
        return f"Не удалось получить комиссию по инструменту {strategy_settings['coin_name']}.\n" \
               f"Ответ сервера: {fee}"
    return str(round(price_round * volume * fee, 5)).rstrip('0').rstrip('.')


@logger.catch()
def open_order(price_round: float, side: str, stop_loss_round: float, strategy_settings: dict,
               take_profit_round: float, volume: float) -> [bool, str | dict]:
    position = Position(strategy_settings['exchange'], strategy_settings['exchange_type'],
                        strategy_settings['coin_name'])
    logger.info(f"order - {side, price_round, volume, stop_loss_round, take_profit_round}")
    # order = position.open_position((side, price_round, volume, stop_loss_round, take_profit_round))
    # if isinstance(position, str):
    #     return False, order
    return position.open_position((side, price_round, volume, stop_loss_round, take_profit_round))


@logger.catch()
def get_orders_list(balance_client: float, coin_info: dict, data_frame: pd.DataFrame, direction: dict, min_lot: float,
                    strategy_settings: dict) -> [bool, list | str]:
    orders = []
    for side in direction.keys():
        open_position_price = get_open_position_price(data_frame, side, strategy_settings)
        logger.info(f"open_position_price - {open_position_price}")
        if not open_position_price:
            return False, f"Не удалось рассчитать цену открытия ордера: {open_position_price}"

        volume = get_largest_volume(balance_client, min_lot, strategy_settings['percentage_deposit'],
                                    open_position_price)
        logger.info(f"volume - {volume}")
        if volume == 0 or isinstance(volume, str):
            return False, f"Не достаточно баланса для открытия позиции.\n" \
                          f"Текущий баланс: {balance_client} USDT\n" \
                          f"Задан процент от депозита: {strategy_settings['percentage']}%\n" \
                          f"Цена инструмента: {open_position_price} USDT\n" \
                          f"Минимально необходимое количество лотов: {min_lot}\n" \
                          f"По имеющимся параметрам хватает на 0 лотов."

        stop_loss_usd, take_profit_usd = calculation_stop_take_usd(balance_client, data_frame, strategy_settings,
                                                                   volume)
        logger.info(f"\nstop_loss_usd - {stop_loss_usd}\ntake_profit_usd - {take_profit_usd}")
        if not stop_loss_usd:
            return False, f"Не хватает необходимых данных для открытия позиции\n" \
                          f"Stop_loss: {strategy_settings['stop_loss']}\n" \
                          f"Take_profit: {strategy_settings['take_profit']}"

        stop_loss, take_profit = calculation_stop_take(side, open_position_price, stop_loss_usd, take_profit_usd)
        logger.info(f"\nstop_loss - {stop_loss}\ntake_profit - {take_profit}")

        rounding_accuracy_price = get_rounding_accuracy(coin_info["result"]['list'][0]['priceFilter']['tickSize'])
        price_round = str(round(open_position_price, rounding_accuracy_price))
        stop_loss_round = str(round(stop_loss, rounding_accuracy_price))
        take_profit_round = str(round(take_profit, rounding_accuracy_price))
        order = open_order(price_round, side, stop_loss_round, strategy_settings, take_profit_round, volume)
        if isinstance(order, str):
            return False, order

        orders.append(order)
    return True, orders


@logger.catch()
def fractal_strategy(strategy_settings: dict) -> [bool, None | str | list]:
    data_frame = add_data_frame(strategy_settings)
    # logger.info(f"add_data_frame - \n{data_frame}")
    data_frame = add_fractals_indicator(data_frame, strategy_settings['period'])
    # logger.info(f"add_fractals_indicator - \n{data_frame}")
    direction = direction_determination(data_frame)
    logger.info(f"direction - {direction}")
    if not direction:
        return False, None

    signals = signal_open_position(data_frame, direction)
    logger.info(f"signals - {signals}")
    if not signals:
        return False, None

    data_frame = add_average_true_range_period(data_frame, strategy_settings['period'])
    # logger.info(f"add_average_true_range_period - \n{data_frame}")
    balance_client = Client(strategy_settings['exchange'], strategy_settings['exchange_type'],
                            strategy_settings['coin_name']).get_balance()
    logger.info(f"balance_client - {balance_client}")
    if isinstance(balance_client, str):
        return False, f"Не удалось получить баланс клиента.\nОтвет сервера: {balance_client}"

    coin_info = get_instrument_info_bybit('linear', strategy_settings['coin_name'])
    # logger.info(f"coin_info - {coin_info}")
    if isinstance(coin_info, str) or not coin_info:
        return False, f"Не удалось получить данные по инструменту {strategy_settings['coin_name']}.\n" \
                      f"Ответ сервера: {coin_info}"

    min_lot = coin_info["result"]['list'][0]['lotSizeFilter']['minOrderQty']
    logger.info(f"min_lot - {min_lot}")

    return get_orders_list(balance_client, coin_info, data_frame, direction, min_lot, strategy_settings)


@logger.catch()
def get_largest_volume(balance_client: float, position_min_quantity: str, percentage_deposit: float,
                       price: float) -> float:
    try:
        decimal_places = get_rounding_accuracy(position_min_quantity)
        return round(balance_client * percentage_deposit / 100 / price, decimal_places)
    except ZeroDivisionError:
        return


@logger.catch()
def get_rounding_accuracy(tick_size: str) -> int:
    if tick_size.find('.') > 0:
        return tick_size.split('.')[-1].find('1') + 1
    return


if __name__ == '__main__':
    logger.info('Running fractals.py from module strategies')
