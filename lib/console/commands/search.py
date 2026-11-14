# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from apps.utility.colors import *
from apps.utility.load_db import search_modules


# Search command to search for the modules we want to search for
# This is very dynamic as in general it does not require specific words.
# if there is a module name scan_a, scan_b, and you run it like;
#
# Command => search <value>
#
# then all module names containing the word scan will appear completely.
def execute(args, ctx):
    query = " ".join(args) if args else ""

    if not query:
        smf.printf(f"{CC.YELLOW}[!] Enter file name to search!{CC.RESET}")
    else:
        search_modules(query)
