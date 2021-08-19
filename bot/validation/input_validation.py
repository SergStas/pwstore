from logger.Logger import Logger


def validate_class(value: str) -> bool:  # TODO: validation
    return __todo(value)


def validate_lvl(value: str) -> bool:
    try:
        int(value)
        return True
    except Exception as e:
        Logger.error(f'Invalid lvl value on new lot session"\n\t\t\t{e}')
        return False


def validate_heaven(value: str) -> bool:
    return __todo(value)


def validate_doll(value: str) -> bool:
    return __todo(value)


def validate_description(value: str) -> bool:
    return __todo(value)


def validate_price(value: str) -> bool:
    try:
        float(value)
        return True
    except Exception as e:
        Logger.error(f'Invalid price value on new lot session"\n\t\t\t{e}')
        return False


def validate_contacts(value: str) -> bool:
    return __todo(value)


def __todo(value):
    return str is not None and len(value) > 0
