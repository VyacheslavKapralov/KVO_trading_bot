from typing import Any, Generator

from loguru import logger

from binance_api.actions_with_positions.close_position import close_position
from binance_api.client_information.get_positions import get_positions_futures
from binance_api.actions_with_positions.open_position import open_position


@logger.catch()
def action_choice(coin, exchange_type, position_side, percentage_deposit):
    positions = all_positions(coin, exchange_type)

    if not positions:
        result = open_position(coin, exchange_type, position_side, percentage_deposit)
        return True, result

    for elem in positions:
        if positions and elem.get('positionSide') != position_side:
            close_position(coin, exchange_type, position_side=elem.get('positionSide'),
                           quantity=float(elem.get('positionAmt')))
            result = open_position(coin, exchange_type, position_side, percentage_deposit)
            return True, result

        else:
            return False, positions


@logger.catch()
def all_positions(coin: str, exchange_type: str) -> Generator[Any, Any, None]:
    if exchange_type == "FUTURES":
        positions = get_positions_futures()
    else:
        positions = None

    return (val for val in positions if val.get('symbol') == coin)


if __name__ == '__main__':
    logger.info('Running strategy.py from module binance_api')

    # res = {'symbol': 'BTCUSDT', 'initialMargin': '122.69808255', 'maintMargin': '0.49079233',
    #        'unrealizedProfit': '11.27517021', 'positionInitialMargin': '122.69808255', 'openOrderInitialMargin': '0',
    #        'leverage': '1', 'isolated': True, 'entryPrice': '27855.72808642', 'maxNotional': '5.0E8',
    #        'positionSide': 'LONG', 'positionAmt': '0.004', 'notional': '122.69808255', 'isolatedWallet': '110.36186195',
    #        'updateTime': 1688371200422, 'bidNotional': '0', 'askNotional': '31.79999000'}
