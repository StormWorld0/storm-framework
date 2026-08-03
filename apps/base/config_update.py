# --- https://github.com/StormWorld0/storm-framework
# --- SMF License
# --- Author: zxelzy

import requests
import json
import os
import smf

from apps.utility.colors import *
from rootmap import ROOT


def check_update():
    # Url to github data json
    url = "https://raw.githubusercontent.com/StormWorld0/storm-framework/main/data/data.json"
    try:  # Request get data json
        latest_version = requests.get(url, timeout=0.8).json()["version"]
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

    except requests.exceptions.RequestException as e:
        smf.printd("ERROR CONNECTION CHECK UPDATE =>", e, level="ERROR")
    except Exception as e:
        smf.printd("ERROR CHECK UPDATE", e, level="ERROR")
