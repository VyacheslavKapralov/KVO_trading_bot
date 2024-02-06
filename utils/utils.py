from loguru import logger


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
    logger.info('Running utils.py from module utils')
