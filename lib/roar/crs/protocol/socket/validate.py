def _is_strict_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_optional_str(value: object, name: str) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a str or None, got {type(value).__name__}")
    return value


def _validate_optional_int(value: object, name: str) -> int | None:
    if value is None:
        return None
    if not _is_strict_int(value):
        raise TypeError(f"{name} must be an int or None, got {type(value).__name__}")
    return value


def _parse_optional_port(value: object) -> int | None:
    if value is None:
        return None
    if _is_strict_int(value):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        final_bool = stripped.isascii() and stripped.isdigit()
        if not final_bool:
            raise ValueError("port string must not be empty")
        try:
            return int(stripped, 10)
        except ValueError as exc:
            raise ValueError(f"port cannot be converted to int: {value!r}") from exc
    raise TypeError(
        f"port must be an int, numeric str, or None, got {type(value).__name__}"
    )


def parse_addr(addr: object) -> tuple[str | None, int | None, int | None, int | None]:
    if not isinstance(addr, tuple):
        raise TypeError("Address must be a tuple")

    if len(addr) == 2:
        host, port = addr
        flowinfo, scope_id = None, None
    elif len(addr) == 4:
        host, port, flowinfo, scope_id = addr
    else:
        raise ValueError(f"Address tuple must have 2 or 4 elements, got {len(addr)}")

    parsed_host = _validate_optional_str(host, "host")
    parsed_port = _parse_optional_port(port)
    parsed_flowinfo = _validate_optional_int(flowinfo, "flowinfo")
    parsed_scope_id = _validate_optional_int(scope_id, "scope_id")

    if parsed_host is None and parsed_port is None:
        raise ValueError("At least one of 'host' or 'port' must be provided")

    return (parsed_host, parsed_port, parsed_flowinfo, parsed_scope_id)


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
