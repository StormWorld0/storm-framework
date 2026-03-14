import os
import importlib
from rootmap import ROOT

"""
utils.py It all contains help logic to make it easier during repairs and updates.
This is included in the core category which cannot be modified.
"""


# LOGIC GLOBAL WORDLIST
def resolve_path(kata_kunci):
    if not kata_kunci:
        return None
    assets_dir = os.path.join(ROOT, "assets/wordlist")

    # Check manual input first
    if os.path.exists(kata_kunci):
        return os.path.abspath(kata_kunci)

    # Search in assets
    if os.path.exists(assets_dir):
        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                if kata_kunci.lower() in file.lower():
                    return os.path.join(root, file)
    return None


# LOGIC SEARCHING & USE
def load_module_dynamically(module_name):
    base_path = os.path.join(ROOT, "modules")

    for root, dirs, files in os.walk(base_path):
        for file in files:
            name_without_ext, ext = os.path.splitext(file)

            if name_without_ext == module_name and ext == ".py":
                full_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_file_path, ROOT)

                if relative_path.endswith(".py"):
                    clean_path = relative_path[:-3]
                else:
                    clean_path = relative_path

                module_dots = clean_path.replace(os.sep, ".")

                try:
                    return importlib.import_module(module_dots)
                except Exception as e:
                    print(f"[-] Error: {e}")
                    return None

    return None


# UI MODULES
EXT = (".py", ".go", ".rs", ".c", ".cpp", ".rb", ".php", ".sh", ".js", ".ts", ".html")


def count_modules():
    total = 0
    # Get absolute root path
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

    # Take the folder directly under /modules (as the main category)
    categories = [
        d
        for d in os.listdir(modules_path)
        if os.path.isdir(os.path.join(modules_path, d))
    ]

    for cat in categories:
        cat_full_path = os.path.join(modules_path, cat)
        count = 0
        # Count files in the category folder (recursive)
        for root, dirs, files in os.walk(cat_full_path):
            for file in files:
                if file.endswith(EXT) and file != "__init__.py":
                    count += 1

        # Add to dictionary if the folder contains modules
        if count > 0:
            stats[cat] = count

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


def get_modules_in_category(category):
    """Retrieves all .py files within a specified category"""
    category_path = os.path.join(ROOT, "modules", category)
    modules_list = []

    if os.path.isdir(category_path):
        for root, dirs, files in os.walk(category_path):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    # Get the path relative to the root modules folder
                    rel_path = os.path.relpath(
                        os.path.join(root, file), os.path.join(ROOT, "modules")
                    )
                    modules_list.append(rel_path.replace(".py", ""))
    return modules_list
