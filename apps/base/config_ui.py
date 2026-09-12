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
  use                           : To use the module, you can use <module_name> or <path_module>
  set <var> <val>               : Filling values in variables
  unset <var>                   : Delete value in a specific variable
  unset all                     : Delete values in all variables
  run                           : Run the selected module

{CC.CYAN}
DATABASE
{CC.MAGENTA}--------
{CC.YELLOW}
  db_status                     : View PostgreSQL database connection status
  db_connect                    : Connect to an external PostgreSQL database manually.
                                  Use the argument format: uname:pass@host:port/db
  db_disconnect                 : Serves to cleanly disconnect the database connection

{CC.CYAN}
WORKSPACE
{CC.MAGENTA}---------
{CC.YELLOW}
  workspace                     : Displays currently available workspaces and hosts
  workspace add <ws_name>       : Adding a new workspace
  workspace del <ws_name>       : Deleting a specific workspace
  workspace <ws_name>           : Move to another workspace (if any)

{CC.CYAN}
DATA
{CC.MAGENTA}----
{CC.YELLOW}
  services                      : Displays service data stored in the Postgres database
  vulns                         : Displays vulnerability data stored in the Postgres database
  hosts                         : Displays host data stored in the Postgres database
  creds                         : Displays credentials stored in the Postgres database

{CC.CYAN}
PLUGIN
{CC.MAGENTA}------
{CC.YELLOW}
  load <plugin_name>            : Loading plugins into memory
  unload <plugin_name>          : Remove plugins from memory
  show plugin                   : Displays existing plugins & plugin status

{CC.CYAN}
UTILITY
{CC.MAGENTA}-------
{CC.YELLOW}
  show options                  : View the variables that have been set
  show modules                  : Displaying module categories
  show wordlist                 : Displays a list of available wordlists
  show <categories>             : Displays the complete contents
  log export <val>              : Export logs from internal database and save as txt
  log dump                      : Dump logs to the terminal screen
  info <module_name>            : Complete Modules information
  search <module_name>          : To search for modules, you can also use
                                  filters such as (act:...) / (defact:...) /
                                  (severity:...) / (cve:...) / (author:...)

{CC.CYAN}
SYSTEM
{CC.MAGENTA}------
{CC.YELLOW}
  help                          : Displaying the manual
  about                         : Information Development
  back                          : Back from current position
  clear                         : Clear command line
  exit                          : Exit the application
  restart                       : To restart if you experience a bug or error
  storm update                  : Make updates if necessary
{CC.RESET}
{CC.GREEN}
COMMAND OUTSIDE
{CC.MAGENTA}---------------
{CC.CYAN}  Can run external tools such as: nuclei, nmap, ping, etc.
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
