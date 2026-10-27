def is_tuple(value) -> bool:
    if isinstance(value, tuple):
        if len(value) != 2:
            raise ValueError("Host tuple only accepts 2 elements: (host, port)")
        return True
    return False
