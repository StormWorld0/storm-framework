def is_tuple2(value) -> bool:
    if isinstance(value, tuple):
        if len(value) != 2:
            raise ValueError("Host tuple only accepts 2 elements: (host, port)")
        return True
    return False


def is_inflo(value) -> bool:
    if not isinstance(value, (float, int)):
        raise ValueError("Timeout must use float or int.")
    return True
