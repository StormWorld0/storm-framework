def parse_addr(addr: object) -> tuple[str | None, int | None, int | None, int | None]:
    if type(addr) is not tuple:
        raise TypeError("Address must be a tuple")

    n = len(addr)
    if n == 2:
        host, port = addr
        flowinfo = scope_id = None
    elif n == 4:
        host, port, flowinfo, scope_id = addr
    else:
        raise ValueError("Address tuple must have 2 or 4 elements")

    if host is None or host == "":
        host = None
    elif type(host) is not str:
        raise TypeError("host must be a str or None")

    if port is None:
        pass
    elif type(port) is int:
        pass
    elif type(port) is str:
        s = port.strip()
        if not s:
            raise ValueError("port string must not be empty")
        try:
            port = int(s, 10)
        except ValueError as exc:
            raise ValueError("port cannot be converted to int") from exc
    else:
        raise TypeError("port must be an int, numeric str, or None")

    if flowinfo is not None and type(flowinfo) is not int:
        raise TypeError("flowinfo must be an int or None")

    if scope_id is not None and type(scope_id) is not int:
        raise TypeError("scope_id must be an int or None")

    if host is None and port is None:
        raise ValueError("At least one of 'host' or 'port' must be provided")

    return (host, port, flowinfo, scope_id)


def is_tuple2(value) -> bool:
    if isinstance(value, bool):
        raise TypeError("Boolean is not a valid address")
    if isinstance(value, tuple):
        if len(value) != 2:
            raise ValueError("address tuple only")
        return True
    raise TypeError("address must be a tuple")


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
