import smf
import sys
from .manager import BinaryManager
from ...smf.exception import SMFFileNotFoundError

IS_WINDOWS = sys.platform.startswith("win")
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux") or hasattr(sys, "getandroidapilevel")


def resolve_bin_path(query_name: str) -> str:
    smf.printd(f"Resolving path for binary", query_name, level="DEBUG")
    bm = BinaryManager()

    # 1. Exact Match
    exact_path = bm._query_db("filename", query_name)
    if exact_path:
        return exact_path

    # 2. OS-Aware Smart Fallback
    candidates = []
    if IS_WINDOWS:
        candidates = [
            f"{query_name}.pyd",
            f"{query_name}.dll",
            f"{query_name}.exe",
            f"{query_name}",
        ]
    elif IS_MACOS:
        candidates = [
            f"{query_name}.dylib",
            f"lib{query_name}.dylib",
            f"{query_name}.so",
            f"{query_name}",
        ]
    elif IS_LINUX:
        candidates = [
            f"{query_name}.so",
            f"lib{query_name}.so",
            query_name,
        ]

    for candidate in candidates:
        candidate_path = bm._query_db("filename", candidate)
        if candidate_path:
            return candidate_path

    # Stem Fallback Match
    stem_path = bm._query_db("stem", query_name)
    if stem_path:
        smf.printd(
            f"Resolved via pure stem fallback: {query_name}",
            stem_path,
            level="DEBUG",
        )
        return stem_path

    smf.printd(
        f"Resolution failed for {query_name}.",
        candidates,
        level="ERROR",
    )
    raise SMFFileNotFoundError(f"Binary '{query_name}' not found for current OS.")
