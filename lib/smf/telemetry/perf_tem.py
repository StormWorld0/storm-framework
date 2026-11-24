import smf
import time
from functools import wraps
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable[..., object])


def format_duration(elapsed_ns: int) -> str:
    if elapsed_ns < 1_000:
        return f"{elapsed_ns:g} ns"
    if elapsed_ns < 1_000_000:
        return f"{elapsed_ns / 1_000:g} µs"
    return f"{elapsed_ns / 1_000_000:g} ms"


def trace_ms(func: F, *, log_fn: Callable[[str], None] = print) -> F:
    """Record the function execution duration in milliseconds (ms)"""
    perf_counter_ns = time.perf_counter_ns

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_ns = perf_counter_ns()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed_ms = format_duration((perf_counter_ns() - start_ns) / 1_000_000)
            smf.printd(
                "Logic performance in ms",
                f"{func.__qualname__}: {elapsed_ms}",
                level="INFO",
            )

    return wrapper  # type: ignore[return-value]
