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


# Extensions wordlist
EXT = (".txt", ".json")


def resolve_wordlist():
    word = os.path.join(ROOT, "assets", "wordlist")
    if not os.path.isdir(word):
        return []
        
    word_var = []
    
    for root, dirs, files in os.walk(word):
        for f in files:
            if f.endswith(EXT):
                word_var.append(os.path.join(dirs, f).lstrip("/"))

    return word_var


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
