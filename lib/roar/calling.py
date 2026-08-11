# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import sys
import ctypes
import importlib.util
import smf

from .callbin.manager import _query_db

IS_WINDOWS = sys.platform.startswith("win")
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux") or hasattr(sys, "getandroidapilevel")


def resolve_bin_path(query_name: str) -> str:
    smf.printd(f"Resolving path for", query_name, level="DEBUG")

    # 1. Exact Match
    exact_path = _query_db("filename", query_name)
    if exact_path:
        return exact_path

    # 2. OS-Aware Smart Fallback
    candidates = []
    if IS_WINDOWS:
        candidates = [
            f"{query_name}.pyd",
            f"{query_name}.dll",
            f"{query_name}.exe",
        ]
    elif IS_MACOS:
        candidates = [
            f"{query_name}.dylib",
            f"lib{query_name}.dylib",
            f"{query_name}.so",
        ]
    elif IS_LINUX:
        candidates = [
            f"{query_name}.so",
            f"lib{query_name}.so",
            query_name,
        ]

    for candidate in candidates:
        candidate_path = _query_db("filename", candidate)
        if candidate_path:
            return candidate_path

    # Stem Fallback Match
    stem_path = _query_db("stem", query_name)
    if stem_path:
        smf.printd(
            f"Resolved via pure stem fallback: {query_name} ->",
            stem_path,
            level="DEBUG",
        )
        return stem_path

    smf.printd(
        f"Resolution failed for {query_name}. Candidates tried:",
        candidates,
        level="ERROR",
    )
    raise FileNotFoundError(
        f"Binary or Shared Object '{query_name}' not found for current OS."
    )


def call_bin(query_name: str) -> str:
    """To call the binary executable"""
    return resolve_bin_path(query_name)


def call_cty(query_name: str) -> ctypes.CDLL:
    """
    ONLY use this for pure C/C++ libraries.
    Do not use for PyO3/Cython modules.
    """
    lib_path = resolve_bin_path(query_name)
    try:
        smf.printd(f"Loading shared object via ctypes", lib_path, level="INFO")
        return ctypes.CDLL(lib_path)
    except OSError as e:
        smf.printd(
            f"Failed to load shared library '{lib_path}' into memory.",
            e,
            level="CRITICAL",
        )
        raise


def call_so(query_name: str, module_name: str = None):
    """
    The native loader uses importlib to execute CPython Extension (PyO3).
    This triggers PyInit_<modulename> so the module can be used immediately.
    """
    stem = query_name.split(".")[0]
    module_name = module_name or stem

    if module_name is None:
        module_name = query_name

    if module_name in sys.modules:
        return sys.modules[module_name]

    lib_path = resolve_bin_path(query_name)
    try:
        smf.printd(
            f"Loading Python Extension module: {module_name} from",
            lib_path,
            level="INFO",
        )
        spec = importlib.util.spec_from_file_location(module_name, lib_path)
        if spec is None:
            raise ImportError(f"Cannot create spec for {lib_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        smf.printd(f"Failed to load Python extension '{lib_path}'", e, level="CRITICAL")
        raise RuntimeError(f"Error exception: {e}")
