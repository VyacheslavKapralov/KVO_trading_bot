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
def direction_determination(data: pd.DataFrame) -> tuple[str, float] | dict[str: float]:  # ToDO: дописать еще условий для определения направления позиции
    highs = find_last_fractals(data, 'Up_Fractal', 2)
    downs = find_last_fractals(data, 'Down_Fractal', 2)
    try:
        if highs[1] >= highs[0] and downs[1] >= downs[0]:
            return  # {'Buy': downs[1], 'Sell': highs[1]}
        elif highs[0] > highs[1] and downs[0] >= downs[1]:
            return tuple('Buy', downs[1])
        elif highs[0] <= highs[1] and downs[0] < downs[1]:
            return tuple('Sell', highs[1])
    except IndexError as error:
        return


@logger.catch()
def signal_open_position(data: pd.DataFrame, side: str, price_indicator: float) -> bool:
    high = data.tail(1)['High'].values[0]
    low = data.tail(1)['Low'].values[0]

    if side == 'Sell' and high > price_indicator:
        return True
    if side == 'Buy' and low < price_indicator:
        return True
    return False


@logger.catch()
def get_open_position_price(data: pd.DataFrame, side: str, strategy_settings: dict) -> float | None:
    logger.info(f"Down - {find_last_fractals(data, 'Down_Fractal', 1)[0]}")
    logger.info(f"Up - {find_last_fractals(data, 'Up_Fractal', 1)[0]}")
    logger.info(f"rollback - {strategy_settings['rollback']}")

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
def fractal_strategy(strategy_settings: dict) -> [bool, None | str | dict]:
    data_frame = add_data_frame(strategy_settings)
    # logger.info(f"add_data_frame - \n{data_frame}")

    data_frame = add_fractals_indicator(data_frame, strategy_settings['period'])
    # logger.info(f"add_fractals_indicator - \n{data_frame}")

    direction = direction_determination(data_frame)
    # logger.info(f"direction - {direction}")
    if not direction:
        return False, None

    if not signal_open_position(data_frame, direction[0], direction[1]):
        return False, None

    data_frame = add_average_true_range_period(data_frame, strategy_settings['period'])
    # logger.info(f"add_average_true_range_period - \n{data_frame}")

    open_position_price = get_open_position_price(data_frame, direction[0], strategy_settings)
    # logger.info(f"open_position_price - {open_position_price}")

    if not open_position_price:
        return False, f"Не удалось рассчитать цену открытия ордера: {open_position_price}"

    balance_client = Client(strategy_settings['exchange'], strategy_settings['exchange_type'],
                            strategy_settings['coin_name']).get_balance()
    # logger.info(f"balance_client - {balance_client}")

    if isinstance(balance_client, str):
        return False, f"Не удалось получить баланс клиента.\nОтвет сервера: {balance_client}"

    # fee = get_fee_bybit('linear', strategy_settings['coin_name'])['result']['list'][0]['makerFeeRate']
    # logger.info(f"fee - {fee}")
    #
    # if isinstance(fee, str):
    #     return False, f"Не удалось получить комиссию по инструменту {strategy_settings['coin_name']}.\n" \
    #                   f"Ответ сервера: {fee}"
    # fee_total = str(round(price_round * volume * fee, 5)).rstrip('0').rstrip('.')

    coin_info = get_instrument_info_bybit('linear', strategy_settings['coin_name'])
    # logger.info(f"coin_info - {coin_info}")

    if isinstance(coin_info, str) or not coin_info:
        return False, f"Не удалось получить данные по инструменту {strategy_settings['coin_name']}.\n" \
                      f"Ответ сервера: {coin_info}"

    min_lot = coin_info["result"]['list'][0]['lotSizeFilter']['minOrderQty']
    volume = get_largest_volume(balance_client, min_lot, strategy_settings['percentage_deposit'], open_position_price)
    # logger.info(f"volume - {volume}")
    if isinstance(volume, str):
        return False, volume

    match strategy_settings['stop_loss_selection'], strategy_settings['take_profit_selection']:
        case 'atr', 'atr':
            stop_loss_usd = data_frame[f"ATR_{strategy_settings['period']}"].iloc[-1]
            take_profit_usd = stop_loss_usd * strategy_settings['multiplicity_atr']
        case 'atr', 'percent':
            stop_loss_usd = data_frame[f"ATR_{strategy_settings['period']}"].iloc[-1]
            take_profit_usd = balance_client * strategy_settings['take_profit'] / 100
        case 'atr', 'usdt':
            stop_loss_usd = data_frame[f"ATR_{strategy_settings['period']}"].iloc[-1]
            take_profit_usd = strategy_settings['take_profit'] / volume
        case 'percent', 'percent':
            stop_loss_usd = balance_client * strategy_settings['stop_loss'] / 100
            take_profit_usd = balance_client * strategy_settings['take_profit'] / 100
        case 'percent', 'atr':
            stop_loss_usd = balance_client * strategy_settings['stop_loss'] / 100
            take_profit_usd = data_frame[f"ATR_{strategy_settings['period']}"].iloc[-1] * strategy_settings[
                'multiplicity_atr']
        case 'percent', 'usdt':
            stop_loss_usd = balance_client * strategy_settings['stop_loss'] / 100
            take_profit_usd = strategy_settings['take_profit'] / volume
        case 'usdt', 'usdt':
            stop_loss_usd = strategy_settings['stop_loss'] / volume
            take_profit_usd = strategy_settings['take_profit'] / volume
        case 'usdt', 'atr':
            stop_loss_usd = strategy_settings['stop_loss'] / volume
            take_profit_usd = data_frame[f"ATR_{strategy_settings['period']}"].iloc[-1] * strategy_settings[
                'multiplicity_atr']
        case 'usdt', 'percent':
            stop_loss_usd = strategy_settings['stop_loss'] / volume
            take_profit_usd = balance_client * strategy_settings['take_profit'] / 100
        case _:
            return False, f"Не хватает необходимых данных для открытия позицииЖ\n" \
                          f"Stop_loss: {strategy_settings['stop_loss']}\n" \
                          f"Take_profit: {strategy_settings['take_profit']}"

    if direction[0] == 'Buy':
        stop_loss = open_position_price - stop_loss_usd
        take_profit = open_position_price + take_profit_usd
    else:
        stop_loss = open_position_price + stop_loss_usd
        take_profit = open_position_price - take_profit_usd

    rounding_accuracy_price = get_rounding_accuracy(coin_info["result"]['list'][0]['priceFilter']['tickSize'])
    price_round = str(round(open_position_price, rounding_accuracy_price))
    stop_loss_round = str(round(stop_loss, rounding_accuracy_price))
    take_profit_round = str(round(take_profit, rounding_accuracy_price))

    sent_order = {}
    position = Position(strategy_settings['exchange'], strategy_settings['exchange_type'],
                        strategy_settings['coin_name'])
    for elem in direction:
        logger.info(f"order - {elem, price_round, stop_loss_round, take_profit_round}")
        sent_order.update(position.open_position((elem, price_round, stop_loss_round, take_profit_round)))
    return True, sent_order


@logger.catch()
def get_largest_volume(balance_client: float, position_min_quantity: str, percentage_deposit: float,
                       price: float) -> float:
    try:
        decimal_places = get_rounding_accuracy(position_min_quantity)
        return round(balance_client * percentage_deposit / 100 / price, decimal_places)
    except ZeroDivisionError:
        return "Недостаточно средств на балансе."


@logger.catch()
def get_rounding_accuracy(tick_size: str) -> int:
    if tick_size.find('.') > 0:
        return tick_size.split('.')[-1].find('1') + 1
    return


if __name__ == '__main__':
    logger.info('Running fractals.py from module strategies')
