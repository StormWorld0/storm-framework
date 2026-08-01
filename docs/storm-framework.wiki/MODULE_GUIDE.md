# Storm Framework Module Guide Explanation 

How to add a module in Storm is a bit easy like copy -> write -> run, and the module will automatically be loaded and ready to use. We use Dynamic Loading mechanism to load only when called.

## information template

You just need to know that Storm uses the Python orchestrator, and the module is also dynamic because we can use even low-level languages for tool efficiency and run it as a subprocess or whatever, as long as Python is running it.

### 1. **Metadata module:**

This is important as metadata to make it easier to find descriptions of modules and other information.

```python
metadata = {
    # Unique Identification & Attribution Module
    "Name": "Module Name",
    "Description": """
Complete explanation of what this module does, its impact, and its scope.
    """,
    "Author": ["Your Name"],
    "License": "SMF LICENSE",
    "Date": "YYYY-MM-DD",
    "Action": [
        ["action name", {"Description": "brief explanation"}],
        ["action name", {"Description": "brief explanation"}],
    ],
    "DefaultAction": "default action name",

    # Vulnerability Intelligence (optional)
    "Vulnerability": {
        "CVE": "CVE-XXXX-XXXX",
        "Severity": "CRITICAL",  # CRITICAL/HIGH/MEDIUM/LOW
        "Published": "YYYY-MM-DD",
        "Updated": "YYYY-MM-DD",
        "References": ["https://nvd.nist.gov/vuln/detail/CVE-XXXX-XXXX"]
    }
}
```

### 2. **Standard Options:**

Just adjust it to what your module needs.

```python
REQUIRED_OPTIONS = {
    "IP": "",
    "PORT": "",
    "PASS": "",
    "URL": "",
    "EMAIL": "",
    "HASH": "",
    "MESSAGE": "",
    "USER": "",
    "USERNAME": ""
    "ID": "",
    "COUNT": "",
    "PATH": "",
    "INTERFACE": "",
    "PROTOCOL": "",
    "THREAD": "",
    "DOMAIN": "",
    "HOSTNAME": "",
    "HOST": ""
    "MODULE": "",
    "API": "",
    "KEY": "",
    "SUBDOM": "",
    "SERVER": "",
    "WORD": "",
    "COMMAND": "",
}
```

> [!IMPORTANT]
> **REQUIRED_OPTIONS:** For `PASS`, `SUBDOM` and `PATH` will be automatically directed to `assets/wordlist`,
> So just enter the wordlist name, for example: (`set PASS pasword_unix`) will automatically be
> pathed to `../storm-framework/assets/wordlist/password_unix.txt`.

### 3. **Module Function:**

Make sure to always consistently use the entry point function `def execute(options)` Just use it as an entry point, otherwise you are free to use any function name you want.

```python
# --- Main function ---
def execute(options):

    example = options.get("IP")
    example = options.get("PORT")
    example = options.get("PASS")
    example = options.get("URL")
```

---

## Connection Runtime Service (CRS)

Now the module is only implemented as a template, use CRS to handle connections with high stability and maximum speed. CRS will handle connections according to the required protocol, no longer depending on external libraries so that it is easier when experiencing bugs/errors with the connection being used.

We have made documentation [CRS ENGINE](https://github.com/StormWorld0/storm-framework/blob/main/docs/storm-framework.wiki/CRS_ENGINE.md) You can read it to find out more.

### Implementation

The way to use CRS is to call the API of the required protocol and send data there. Implementation example:

```python
def execute(options, net):
    ip = options.get("IP")
    port = options.get("PORT")

    data = b"0x01..." # Data Bytes
    s = net.Socket(ip, port, timeout=2) # Open connection
    s.send(data, timeout=3) # Send data
    resp = s.recv(1024) # Read buffer

    if resp.status == "SUCCESS":
        smf.printf("Raw Bytes", resp.raw_bytes)
        smf.printf("String Bytes", resp.str_bytes)
        smf.printf("Amount Bytes", resp.read_bytes)
    else:
        smf.printf("Message ERROR/SUCCESS", resp.message)

    cert = path/to/file/cert
    key = path/to/file/key
    ca = path/to/file/ca # Optional

    try:
        # Upgrade TLS connection
        r = s.uptls(cert, key, ca, verify=False)

        # Automatically use TLS connection after upgrade
        s.send()
        s.recv()
    except Exception:
        smf.printf(r.message)
    finally:
        s.close() # Stop the connection so it doesn't hang

    smf.printf("Cipher Suite", r.tls.cipher)
    smf.printf("Version TLS 1.0/1.1/1.2/1.3", r.tls.version)
```

If you want to know what data is issued by the existing protocols, you can see it at [CRS ENGINE DOCS](https://github.com/StormWorld0/storm-framework/blob/main/docs/storm-framework.wiki/CRS_ENGINE.md)



