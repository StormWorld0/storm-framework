# MIT License.
# Copyright (c) 2026 Storm Framework

# See LICENSE file in the project root for full license information.


import requests
from versi import VERSION
from app.utility.colors import C


def check_update():
    # Raw URL to the version.txt file on GitHub
    url = "https://raw.githubusercontent.com/STORM-CORP/storm-framework/main/version.txt"
    try:
        response = requests.get(url, timeout=5)
        latest_version = response.text.strip()
        # If the version on GitHub is higher than the local version
        if latest_version > VERSION:
            print(
                f"{C.SUCCESS}[!] Update available: v{latest_version} | Current version: v{VERSION}"
            )
            print(f"{C.SUCCESS}[-] Type: storm update")
            print("")
    except:
        pass
