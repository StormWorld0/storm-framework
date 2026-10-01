# --- https://github.com/StormWorld0/storm-framework
# --- SMF License
# --- Author: zxelzy

import requests
import json
import os
import smf

from apps.utility.colors import CC
from lib.roar.crs.net_api import HTTPR
from rootmap import ROOT


def check_update():
    # Url to github data json
    url = "https://raw.githubusercontent.com/StormWorld0/storm-framework/main/data/data.json"
    http = HTTPR()
    try:
        http.timeout(0.8)
        http.get(url)
        resp = http.run()
        latest_version = resp.json()["version"]
        
        # Get local json data
        data = os.path.join(ROOT, "data", "data.json")

        # View contents and search for versions
        with open(data) as f:
            VERSION = json.load(f)["version"]

        # Compare current version with github
        if latest_version > VERSION:
            smf.printf(f"{CC.GREEN}[!] Current version => v{VERSION}")
            smf.printf(f"{CC.GREEN}[!] Latest Version  => v{latest_version}")
            smf.printf(f"{CC.GREEN}[-] Type => storm update")
            smf.printf()

    except http.HTrace:
        pass
    except Exception:
        pass
