def is_tuple2(value) -> bool:
    if isinstance(value, tuple):
        if len(value) != 2:
            raise ValueError("address tuple only accepts 2 elements: (host, port)")
        return True
    raise ValueError("address must be a tuple of host and port.")
