import json
import os
import smf

import apps.utility.utils as utils
from apps.utility.colors import CC
from rootmap import ROOT


def show_about():
    data = os.path.join(ROOT, "data", "data.json")
    with open(data) as f:
        VERSION = json.load(f)["version"]

    smf.printf(
        f"\n{CC.MAGENTA}=========================================================================="
    )
    smf.printf(
        f"{CC.MAGENTA}=========================================================================="
    )
    smf.printf(f"{CC.YELLOW}      Tool                      : Storm Framework")
    smf.printf(f"{CC.YELLOW}      Organization              : StormWorld0")
    smf.printf(f"{CC.YELLOW}      Owner                     : エルジー")
    smf.printf(f"{CC.YELLOW}      Purpose                   : All-In-One Pentest Tool")
    smf.printf(f"{CC.YELLOW}      Version                   : {VERSION}")
    smf.printf(
        f"{CC.YELLOW}      Documentation             : https://storm-framework.pages.dev"
    )
    smf.printf(
        f"{CC.YELLOW}      GitHub                    : github.com/StormWorld0/storm-framework"
    )
    smf.printf(
        f"{CC.YELLOW}      DockerHub                 : hub.docker.com/r/stormworld0/storm-framework"
    )
    smf.printf(
        f"{CC.MAGENTA}==========================================================================\n"
    )


def show_help():
    smf.printf(f"""
{CC.MAGENTA}==========================================================================
{CC.GREEN}                             COMMAND GUIDE
{CC.MAGENTA}==========================================================================
{CC.CYAN}
CORE
{CC.MAGENTA}----
{CC.YELLOW}
  use                           : Select and load a module (by name or path)
  set <var> <val>               : Set a value for a specific variable
  unset <var>                   : Clear the value of a specific variable
  unset all                     : Clear all configured variables
  run                           : Execute the currently selected module

{CC.CYAN}
DATABASE
{CC.MAGENTA}--------
{CC.YELLOW}
  db_status                     : Show current PostgreSQL database connection status
  db_connect                    : Manually connect to an external PostgreSQL database
                                  Format: uname:pass@host:port/db
  db_disconnect                 : Cleanly terminate the active database connection

{CC.CYAN}
WORKSPACE
{CC.MAGENTA}---------
{CC.YELLOW}
  workspace                     : Display active workspace and target hosts
  workspace add <ws_name>       : Create a new workspace
  workspace del <ws_name>       : Delete a specified workspace
  workspace <ws_name>           : Switch to another workspace

{CC.CYAN}
DATA
{CC.MAGENTA}----
{CC.YELLOW}
  services                      : Display stored service data from PostgreSQL
  vulns                         : Display stored vulnerability data from PostgreSQL
  hosts                         : Display stored host data from PostgreSQL
  creds                         : Display stored credential data from PostgreSQL

{CC.CYAN}
PLUGIN
{CC.MAGENTA}------
{CC.YELLOW}
  load <plugin_name>            : Load a plugin into memory
  unload <plugin_name>          : Unload a plugin from memory
  show plugin                   : Display available plugins and their current status

{CC.CYAN}
UTILITY
{CC.MAGENTA}-------
{CC.YELLOW}
  show options                  : View all currently set variables
  show modules                  : Display available module categories
  show wordlist                 : List available wordlists
  show <categories>             : Display full contents of a specific category
  log export <val>              : Export logs from internal database to a .txt file
  log dump                      : Dump raw internal logs directly to the terminal
  info <module_name>            : Show detailed information about a module
  search <module_name>          : Search for modules with advanced filter support
                                  Filters: (act:...) / (defact:...) /
                                  (severity:...) / (cve:...) / (author:...)

{CC.CYAN}
SYSTEM
{CC.MAGENTA}------
{CC.YELLOW}
  help                          : Display this command manual
  about                         : Display framework and development metadata
  back                          : Return to the previous menu context
  clear                         : Clear the terminal screen
  exit                          : Exit the application
  restart                       : Restart the framework engine
  storm update                  : Check and install framework updates
{CC.RESET}
{CC.GREEN}
COMMAND OUTSIDE
{CC.MAGENTA}---------------
{CC.CYAN}  Execute external system binaries directly (e.g., nuclei, nmap, ping, etc.)
{CC.RESET}
    """)


def stormUI():
    total = utils.count_modules()
    stats = utils.count_by_category()

    # 1. Create a list containing strings for each category.
    # Example: ["MODULE: 15", "EXPLOIT: 2", "AUXILIARY: 11", "VULNERABILITY: 2"]
    items = [f"MODULE: {total}"] + [f"{k.upper()}: {v}" for k, v in stats.items()]

    # 2. Group items max 3
    max_items_per_row = 3
    for i in range(0, len(items), max_items_per_row):
        row_items = items[i : i + max_items_per_row]

        # 3. Combine only the items in that row with " | "
        line_text = " | ".join(row_items)

        # 4. Decorative print
        smf.printf(
            f"{CC.MAGENTA}+-- --=[ {CC.YELLOW}{line_text} {CC.MAGENTA}]=--{CC.RESET}"
        )

    smf.printf()
    smf.printf(
        f"{CC.WHITE}The Storm Framework is a StormWorld0 Open Source Project{CC.RESET}"
    )
    smf.printf(
        f"{CC.WHITE}Run {CC.GREEN}about{CC.WHITE} to view dev information.{CC.RESET}"
    )
    smf.printf()
