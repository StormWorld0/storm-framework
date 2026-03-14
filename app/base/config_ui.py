import versi as v
import app.utility.utils as utils
from app.utility.colors import C


def show_about():
    print(
        f"\n{C.HEADER}=========================================================================="
    )
    print(
        f"{C.HEADER}=========================================================================="
    )
    print(f"{C.INPUT}      owner                     : Elzy")
    print(f"{C.INPUT}      Contributor               : There isn't any yet")
    print(f"{C.INPUT}      Purpose                   : All-in-One Pentest Tools")
    print(f"{C.INPUT}      Version                   : {v.VERSION}")
    print(
        f"{C.INPUT}      GitHub                    : github.com/StormWorld0/storm-framework"
    )
    print(
        f"{C.HEADER}==========================================================================\n"
    )


def show_help():
    print(f"""
{C.HEADER}==========================================================================
{C.SUCCESS}                             COMMAND GUIDE
{C.HEADER}==========================================================================
{C.INPUT}
  help                          : Displaying the manual
  show options                  : View the variables that have been set
  show modules                  : Displaying module categories
  show <name_categories>        : Displays the complete contents

  search <filename>             : To search for files
  about                         : Information Development
  info <cve_name>               : Complete CVE information
  back                          : Back from current position
  clear                         : Clear command line
  exit                          : Exit the application
{C.INPUT}
  use <nama_modul>              : Selecting a module
  set <key> <val>               : Filling in the parameters
  run                           : Run the selected module

{C.INPUT}
  storm update                  : Make updates if necessary
  storm verify                  : Used to check the signature of all files
  storm restart                 : To restart if you experience a bug or error
{C.HEADER}==========================================================================
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
        print(f"{C.HEADER}+-- --=[ {C.INPUT}{line_text} {C.HEADER}]=--")

    print("")
    print("The Storm Framework is a zxelzy Open Source Project")
    print(f"Run {C.SUCCESS}about{C.RESET} to view dev information.")
    print("")
