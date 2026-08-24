import os
import smf
import importlib

from typing import List
from rootmap import ROOT
from .load_db import *

# utils.py It all contains help logic to make it easier during repairs and updates.
# This is included in the core category which cannot be modified.


# LOGIC GLOBAL WORDLIST
def resolve_path(options):
    if not options:
        return None

    # Input Normalization (Expansion of tilde '~' and env vars like '$HOME')
    normalized_path = os.path.expandvars(os.path.expanduser(options))

    # Explicit Path Validation (Check Absolute path or Current Working Directory)
    if os.path.exists(normalized_path) and os.path.isfile(normalized_path):
        return os.path.abspath(normalized_path)

    normalized_options = options.replace("\\", "/")
    if normalized_options.startswith("wordlist/"):
        # Ambil sisa path setelah "wordlist/" (contoh: "passmini" atau "sub/passmini")
        rel_target = normalized_options[len("wordlist/") :]
        candidate_base = os.path.join(ROOT, "assets", "wordlist", rel_target)

        # 1. Cek match persis (jika user sudah memasukkan ekstensi secara eksplisit)
        if os.path.exists(candidate_base) and os.path.isfile(candidate_base):
            return os.path.abspath(candidate_base)

        # 2. Cek kandidat ekstensi (.txt, .json, dll.)
        EXTENSIONS = ".txt"
        for ext in EXTENSIONS:
            candidate_with_ext = candidate_base + ext
            if os.path.exists(candidate_with_ext) and os.path.isfile(candidate_with_ext):
                return os.path.abspath(candidate_with_ext)

    # Search in Internal wordlist
    assets_dir = os.path.join(ROOT, "assets", "wordlist")

    try:
        if os.path.exists(assets_dir):
            matched_substring_path = None

            for root, dirs, files in os.walk(assets_dir):
                for file in files:
                    file_lower = file.lower()
                    option_lower = options.lower()

                    # Highest Priority: Exact Match
                    if option_lower == file_lower:
                        return os.path.join(root, file)

                    # Save the first substring match result for fallback.
                    if matched_substring_path is None and option_lower in file_lower:
                        matched_substring_path = os.path.join(root, file)

            # If there is no exact match, return the substring match (if any)
            if matched_substring_path:
                return matched_substring_path

    except Exception as e:
        smf.printd("Wordlist utils asset search error", e, level="ERROR")

    # Check directly in $HOME (Only 1 level, NOT recursive os.walk)
    home_dir = os.path.expanduser("~")
    home_target = os.path.join(home_dir, options)

    if os.path.exists(home_target) and os.path.isfile(home_target):
        return os.path.abspath(home_target)

    # Return None if all resolution chains fail
    return None


def resolve_wordlist():
    """Used by show wordlist"""
    word = os.path.join(ROOT, "assets", "wordlist")
    EXT = ".txt"

    if not os.path.isdir(word):
        return []

    results = []
    for root, dirs, files in os.walk(word):
        for file in files:
            if file.endswith(EXT):
                # Remove extension from file name
                file_without_ext, _ = os.path.splitext(file)

                # Relative path construction with file names without extensions
                rel_path = os.path.relpath(os.path.join(root, file_without_ext), word)
                results.append(os.path.join("wordlist", rel_path))

    return results


# LOGIC USE
def load_module_dynamically(module_input):
    # Returns module_path or module_name from DB
    actual_path = resolve_module_path(module_input)

    if not actual_path:
        return None

    # Direct transformation to dot notation for Python import
    module_dots = f"modules.{actual_path.replace('/', '.')}"

    try:
        return importlib.import_module(module_dots)
    except Exception as e:
        smf.printd("ERROR DYNAMIC IMPORT", f"{module_dots} -> {repr(e)}", level="ERROR")
        return None


# UI MODULES
EXT = (".py", ".go", ".rs", ".c", ".cpp", ".rb", ".php", ".sh", ".js", ".ts", ".html")


def count_modules():
    total = 0
    path = os.path.join(ROOT, "modules")
    if not os.path.exists(path):
        return 0

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(EXT) and file != "__init__.py":
                total += 1
    return total


def count_by_category():
    """
    Counting the number of modules based on category folders
    """
    stats = {}
    modules_path = os.path.join(ROOT, "modules")

    if not os.path.exists(modules_path):
        return stats

    categories = [
        d
        for d in os.listdir(modules_path)
        if os.path.isdir(os.path.join(modules_path, d))
    ]

    for cat in categories:
        try:
            cat_full_path = os.path.join(modules_path, cat)
            count = 0

            for root, dirs, files in os.walk(cat_full_path):
                for file in files:
                    if file.endswith(EXT) and file != "__init__.py":
                        count += 1

            if count > 0:
                stats[cat] = count

        except Exception as e:
            smf.printd("Error utils looping over modules category", e, level="ERROR")

    return stats


# LOGIC SHOW
def get_categories():
    """Get a list of category folders inside /modules"""
    modules_path = os.path.join(ROOT, "modules")
    if not os.path.exists(modules_path):
        return []
    return [
        d
        for d in os.listdir(modules_path)
        if os.path.isdir(os.path.join(modules_path, d)) and d != "__pycache__"
    ]


def get_modules_in_category(category: str) -> List[str]:
    """Retrieves all .py files within a specified category"""

    return show_modules(category)
