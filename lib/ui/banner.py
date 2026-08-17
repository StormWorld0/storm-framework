# --- https://github.com/StormWorld0/storm-framework ---
# SMF License
# copyright (c) 2026
# Complete information about the License is in the root directory.
# Author: zxelzy

import os
import smf
import apps.base.config_ui as ui

from apps.base.config_update import check_update
from apps.banners.uib import banner_live


# To clean the terminal before loading anything so it is clean
# load banners to the main interface randomly if more than one banner is available
# Loads main module data statistics for information on the number of available modules
# Check for the latest updates, if any, it will display the latest update information.
def banner():
    try:
        os.system("clear")
        smf.printf(banner_live())
        ui.stormUI()
        check_update()
    except ImportError as e:
        smf.printd("IMPORT BANNER ERROR", e, level="ERROR")
        return
    except Exception as e:
        smf.printd("ERROR BANNER EXCEPTION", e, level="ERROR")
        return
