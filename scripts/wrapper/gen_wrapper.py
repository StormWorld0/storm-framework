import smf
import os
import sys
import ssl

from rootmap import ROOT

from urllib.error import URLError
from urllib.request import Request, urlretrieve, urlopen


# Update wrapper Termux
def Termux():
    url = "https://raw.githubusercontent.com/StormWorld0/storm-framework/main/scripts/wrapper/termux/storm"
    prefix = os.environ.get("PREFIX")
    if not prefix:
        sys.exit(1)
        
    path = os.path.join(prefix, "bin", "storm")

    # Enforce safe TLS context
    context = ssl.create_default_context()
    try:
        req = Request(url, headers={"User-Agent": "storm-framework installer"})
        with urlopen(req, context=context, timeout=15) as response:
            payload = response.read()

        # Write safely to path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(payload)
            
        os.chmod(path, 0o755)

    except URLError as e:
        smf.printf(f"[-] Network error during download: {e.reason}")
    except PermissionError:
        smf.printf(f"[-] Insufficient permissions to write to {target_path}")
    except Exception as e:
        smf.printf("[-] Deployment failed =>", e)


# Update wrapper Linux
def Linux():
    url = "https://raw.githubusercontent.com/StormWorld0/storm-framework/main/scripts/wrapper/linux/storm"
    path = os.path.join(os.sep, "usr", "local", "bin", "storm")
    if not path:
        sys.exit(1)
        
    # Enforce safe TLS context
    context = ssl.create_default_context()
    try:
        req = Request(url, headers={"User-Agent": "storm-framework installer"})
        with urlopen(req, context=context, timeout=15) as response:
            payload = response.read()

        # Write safely to path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(payload)
            
        os.chmod(path, 0o755)

    except URLError as e:
        smf.printf(f"[-] Network error during download: {e.reason}")
    except PermissionError:
        smf.printf(f"[-] Insufficient permissions to write to {target_path}")
    except Exception as e:
        smf.printf("[-] Deployment failed =>", e)


# Update wrapper Venv
def Venv():
    url = "https://raw.githubusercontent.com/StormWorld0/storm-framework/main/scripts/wrapper/venv/storm"
    path = os.path.join(os.sep, "usr", "local", "bin", "storm")
    if not path:
        sys.exit(1)
        
    # Enforce safe TLS context
    context = ssl.create_default_context()
    try:
        req = Request(url, headers={"User-Agent": "storm-framework installer"})
        with urlopen(req, context=context, timeout=15) as response:
            payload = response.read()

        # Write safely to path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(payload)
            
        os.chmod(path, 0o755)

    except URLError as e:
        smf.printf(f"[-] Network error during download: {e.reason}")
    except PermissionError:
        smf.printf(f"[-] Insufficient permissions to write to {target_path}")
    except Exception as e:
        smf.printf("[-] Deployment failed =>", e)




# Entry Point Generator Wrapper
def generate(data):

    if not data:
        sys.exit(1)

    if type == "Termux":
        Termux()
    elif type == "Linux":
        Linux()
    else:
        Venv()


