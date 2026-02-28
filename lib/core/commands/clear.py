# MIT License.
# Copyright (c) 2026 Storm Framework

# See LICENSE file in the project root for full license information.


import os
from app.banners.banner import get_random_banner
import app.base.config_ui as ui


def execute(args, context):
    # Clean the screen according to the OS
    os.system("cls" if os.name == "nt" else "clear")
    # Redisplay tool identity
    print(get_random_banner())
    ui.stormUI()
    return context
