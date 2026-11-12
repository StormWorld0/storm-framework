# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import sys
import ctypes
import importlib.util
import smf
from .callbin.helper import resolve_bin_path
from ..smf.exception import SMFOSError, SMFRuntimeError, SMFImportError


def call_bin(query_name: str) -> str:
    """To call the binary executable"""
    return resolve_bin_path(query_name)


def call_cty(query_name: str) -> ctypes.CDLL:
    """ONLY use this for pure C/C++ libraries."""
    lib_path = resolve_bin_path(query_name)
    try:
        smf.printd(f"Loading ctypes: {query_name}", lib_path, level="INFO")
        return ctypes.CDLL(lib_path)
    except OSError as e:
        smf.printd(
            f"Failed to load shared library '{lib_path}' into memory.",
            e,
            level="ERROR",
        )
        raise SMFOSError(f"Failed load binary ctypes: {lib_path}") from e


def call_so(query_name: str, module_name: str = None):
    """
    The native loader uses importlib to execute CPython Extension (PyO3).
    This triggers PyInit_<modulename> so the module can be used immediately.
    """
    stem = query_name.split(".")[0]
    bin_name = module_name or stem

    if bin_name in sys.modules:
        return sys.modules[bin_name]

    lib_path = resolve_bin_path(query_name)
    try:
        smf.printd(
            f"Loading Python Extension module: {bin_name} from",
            lib_path,
            level="INFO",
        )
        spec = importlib.util.spec_from_file_location(bin_name, lib_path)
        if spec is None:
            raise SMFImportError(f"Cannot create spec for {lib_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[bin_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        smf.printd(f"Failed to load Python extension '{lib_path}'", e, level="ERROR")
        raise SMFRuntimeError(f"Call_so function exception error") from e
