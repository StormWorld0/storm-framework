"""
Make sure you use this template for all the modules you create.
This is the standard that must be set so that all modules can run.
"""

REQUIRED_OPTIONS = {
    "IP": "",
    "PORT": "",
    "PASS": "",
    "URL": "",
    "EMAIL": "",
    "HASH": "",
    "MESSAGE": "",
    "USER": "",
    "ID": "",
    "COUNT": "",
    "PATH": "",
    "INTERFACE": "",
    "THREAD": "",
    "DOMAIN": "",
    "HOSTNAME": "",
    "MODULE": "",
}

"""
For REQUIRED_OPTIONS select what you need.
Make sure the method name for the main function to be executed matches the template's. If it's different, the module won't execute.

"""


# --- Main function ---
def execute(options):

    example = options.get("IP")
    example = options.get("PORT")
    example = options.get("PASS")
    example = options.get("URL")
