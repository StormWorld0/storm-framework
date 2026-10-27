def is_tuple(value) -> bool:
    if isinstance(value, tuple):
        if len(value) != 2:
            return False
        return True
    return False
