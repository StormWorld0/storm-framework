# MIT License.
# Copyright (c) 2026 Storm Framework

# See LICENSE file in the project root for full license information.


import os
import importlib.util
import textwrap
from app.utility.colors import C


# For those who like CVE collections, this logic is definitely needed
# Because this will produce output that is neat in structure and style.
# For ease of reading, and to differentiate between Description, name, ID, etc.
# The most important thing is to make sure that the CVE uses the example data format that has been provided.
# Otherwise the output will be messy and not according to storm rules.
def execute(args, context):
    query = args[0] if args else ""
    if not query:
        print("[-] Enter file name to info!")
        return context

    # This is a special logic to know where the CVE is located.
    # Make sure CVE is always in the vulnerability folder
    vuln_path = "modules/vulnerability/"
    found_path = None
    for root, dirs, files in os.walk(vuln_path):
        if f"{query}.py" in files:
            found_path = os.path.join(root, f"{query}.py")
            break

    if found_path:
        try:
            spec = importlib.util.spec_from_file_location("temp_mod", found_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # --- GET DICTIONARY CVE_INFO ---
            info = mod.CVE_INFO
            width = 55

            print(f"\n{C.HEADER}{'='*width}")
            print(f"{C.SUCCESS}{'STORM VULNERABILITY KNOWLEDGE BASE':^55}")
            print(f"{C.HEADER}{'='*width}")

            print(f"{C.SUCCESS}{'ID CVE':<13} : {info['cve']}")
            print(f"{C.SUCCESS}{'NAME':<13} : {info['name']}")
            print(f"{C.SUCCESS}{'LEVEL':<13} : {info['severity']}")
            print(f"{C.SUCCESS}{'PUBLISHED':<13} : {info['published']}")
            print(f"{C.SUCCESS}{'UPDATED':<13} : {info['updated']}")
            print(f"{C.HEADER}{'-'*width}")

            # Clean Up Description
            print(f"{C.SUCCESS}DESCRIPTION   :")
            desc = textwrap.fill(
                info["description"].strip(),
                width=width - 2,
                initial_indent=" ",
                subsequent_indent=" ",
            )
            print(desc)

            print(f"{C.HEADER}{'-'*width}")
            print(f"{C.SUCCESS}REFERENCES    :")
            for link in info["URL"]:
                print(f" - {link}")
            print(f"{C.HEADER}{'-'*width}")

            print(f"{C.SUCCESS}{'SCANNER':<13} : {info['scanner']}")
            print(f"{C.SUCCESS}{'EXPLOIT':<13} : {info['exploit']}")
            print(f"{C.HEADER}{'='*width}\n")

        except Exception as e:
            print(f"{C.ERROR}[-] Failed to read: {e}")
    else:
        print(f"{C.INPUT}[-] WARN => {query} > not found.")

    return context
