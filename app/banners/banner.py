# MIT License.
# Copyright (c) 2026 Storm Framework

# See LICENSE file in the project root for full license information.


import os
import random
import importlib
from app.utility.colors import C
from rootmap import ROOT


def get_random_banner():
    banner_dir = os.path.join(ROOT, "lib", "ui", "banners")
    try:
        if not os.path.exists(banner_dir):
            return f"{C.SUCCESS}Cyber-Pentest Framework (Folder Not Found)"
        all_files = [
            f
            for f in os.listdir(banner_dir)
            if f.endswith(".py") and f != "__init__.py"
        ]

        if not all_files:
            return f"{C.SUCCESS}Cyber-Pentest Framework"

        random_file = random.choice(all_files)
        module_path = f"lib.ui.banners.{random_file.replace('.py', '')}"

        # Reload module if necessary or import normally
        banner_module = importlib.import_module(module_path)
        raw_banner = getattr(banner_module, "DATA", "Banner data not found.")

        # --- SCREEN MEASUREMENT LOGIC ---
        try:
            columns = os.get_terminal_size().columns
        except:
            columns = 100

        lines = raw_banner.splitlines()
        if not lines:
            return raw_banner

        # Find the longest line to determine the original width of the banner.
        max_banner_width = max(len(line) for line in lines)

        # Hitung jarak spasi dari kiri agar pas di tengah
        padding_size = max(0, (columns - max_banner_width) // 2)
        padding_str = " " * padding_size

        # Rejoin with additional spaces on each line
        centered_banner = "\n".join([f"{padding_str}{line}" for line in lines])

        return centered_banner

    except Exception as e:
        return f"Error loading banner: {e}"
