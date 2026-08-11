import os
from pathlib import Path


def get_cpu_info(core):
    """
    Retrieving CPU information
    total cores, strong cores, capacity.
    """
    capacities = []
    for cpu in range(core):
        path = Path(f"/sys/devices/system/cpu/cpu{cpu}/cpu_capacity")
        try:
            capacity = int(path.read_text().strip())
            capacities.append(capacity)
        except (FileNotFoundError, ValueError):
            pass

    if not capacities:
        return {
            "total": core,
            "strong": core,
        }

    max_capacity = max(capacities)
    threshold = max_capacity * 0.75
    strong_cores = sum(capacity >= threshold for capacity in capacities)

    return {
        "total": core,
        "strong": strong_cores,
    }


def get_make_jobs(total_cores, strong_cores):
    """Determine the number of cores used"""
    ratio = strong_cores / total_cores
    if ratio >= 0.50:
        return round(total_cores * 0.75)
    if ratio >= 0.25:
        return round(total_cores * 0.50)

    return round(total_cores * 0.375)


def safe_mode():
    """Determining the number of CPU cores"""
    term = "TERMUX_VERSION" in os.environ
    core = os.cpu_count() or 1

    if term:
        info = get_cpu_info(core)
        if not info:
            return core

        t = info["total"]
        s = info["strong"]

        cores = get_make_jobs(t, s)
        if not cores:
            return core

        workers = cores
        print(f"[*] Linux detected > {core} cores. Used > {workers} cores")
    else:
        workers = core
        print(f"[*] Linux Standar detected > {workers} cores")

    return workers
