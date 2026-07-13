import json
import os
import smf

import apps.utility.utils as utils
from apps.utility.colors import C
from rootmap import ROOT


def show_about():
    data = os.path.join(ROOT, "data", "data.json")
    with open(data) as f:
        VERSION = json.load(f)["version"]

    smf.printf(
        f"\n{C.HEADER}=========================================================================="
    )
    smf.printf(
        f"{C.HEADER}=========================================================================="
    )
    smf.printf(f"{C.INPUT}      Tool                      : Storm Framework")
    smf.printf(f"{C.INPUT}      Organization              : StormWorld0")
    smf.printf(f"{C.INPUT}      Owner                     : エルジー")
    smf.printf(f"{C.INPUT}      Purpose                   : All-In-One Pentest Tool")
    smf.printf(f"{C.INPUT}      Version                   : {VERSION}")
    smf.printf(
        f"{C.INPUT}      GitHub                    : github.com/StormWorld0/storm-framework"
    )
    smf.printf(
        f"{C.HEADER}==========================================================================\n"
    )


def show_help():
    smf.printf(f"""
{C.HEADER}==========================================================================
{C.SUCCESS}                             COMMAND GUIDE
{C.HEADER}==========================================================================
{C.INPUT}
  show options                  : View the variables that have been set
  show modules                  : Displaying module categories
  show <categories>             : Displays the complete contents
  show plugin                   : Displays existing plugins & plugin status
  info <module_name>            : Complete Modules information
  search <module_name>          : To search for modules, you can also use
                                  filters such as (act:...) / (defact:...) /
                                  (severity:...) / (cve:...) / (author:...)

  help                          : Displaying the manual
  about                         : Information Development
  back                          : Back from current position
  clear                         : Clear command line
  exit                          : Exit the application
  restart                       : To restart if you experience a bug or error
  
  log export <val>              : Export logs from internal database and save as txt
  log dump                      : Dump logs to the terminal screen
  load <plugin_name>            : Loading plugins into memory
  unload <plugin_name>          : Remove plugins from memory
  unset <var>                   : Delete value in a specific variable
  unset all                     : Delete values in all variables

  use                           : To use the module, you can use <module_name> or <path_module>
  set <var> <val>               : Filling values in variables
  run                           : Run the selected module

  storm update                  : Make updates if necessary
{C.RESET}
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
        smf.printf(f"{C.HEADER}+-- --=[ {C.INPUT}{line_text} {C.HEADER}]=--{C.RESET}")

    smf.printf()
    smf.printf("The Storm Framework is a StormWorld0 Open Source Project")
    smf.printf(f"Run {C.SUCCESS}about{C.RESET} to view dev information.")
    smf.printf()
