def is_tuple2(value) -> bool:
    if isinstance(value, tuple):
        if len(value) != 2:
            raise ValueError("address tuple only accepts 2 elements: (host, port)")
        return True
    raise ValueError("address must be a tuple of host and port.")


def parse_flags(*flags):
    result = 0

    def merge(value):
        nonlocal result
        if isinstance(value, bool):
            raise TypeError("Boolean is not a valid flags")
        if isinstance(value, int):
            result |= value
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                merge(item)
            return
        raise TypeError(f"Flags must be integers, list, or tuple")

    for flag in flags:
        merge(flag)
    return result
