# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import apps.utility.utils as utils
from apps.utility.colors import CC


# The show command is used to display data in modules.
# such as the following example;
# 1. Command => show modules > will display the modules category.
# 2. Command => show auxiliary > will display all contents in the auxiliary.
# 3. Command => show options > will display global variables.
# 4. Command => show plugin > will display all existing plugins.
# 5. Command => show wordlist > Will display the available wordlist
def execute(args, ctx):
    target_show = args[0].lower() if args else ""

    current_module = ctx.current_module
    current_module_name = ctx.current_module_name
    options = ctx.options
    plugin = ctx.plugin

    if not target_show:
        smf.printf(f"{CC.YELLOW}[!] No modules selected.{CC.RESET}")
        return

    # 1. show modules
    if target_show == "modules":
        categories = utils.get_categories()

        smf.printf()
        smf.printf(f"[ {CC.CYAN}--- Categories ---{CC.RESET} ]")
        smf.printf()

        for cat in categories:
            smf.printf(f"  - {CC.YELLOW}{cat}{CC.RESET}")

        smf.printf()

    # 2. show options
    elif target_show == "options":
        header_name = current_module_name if current_module else "GLOBAL"

        smf.printf()
        smf.printf(f"{CC.YELLOW}MODULE OPTIONS{CC.RESET} ({header_name})")
        smf.printf()
        smf.printf(
            f"{CC.CYAN}{'Name':<12} {'Current Setting':<25} {'Description'}{CC.RESET}"
        )
        smf.printf(f"{CC.MAGENTA}{'-'*12} {'-'*25} {'-'*15}{CC.RESET}")

        if current_module:
            req = getattr(current_module, "REQUIRED_OPTIONS", {})

            for var_name, desc in req.items():
                val = options.get(var_name, "unset")
                smf.printf(f"{CC.YELLOW}{var_name:<12} {val:<25}{CC.RESET} {desc}")
        else:
            for k, v in options.items():
                val = v if v else "unset"
                smf.printf(f"{CC.YELLOW}{k:<12} {val:<25}{CC.RESET} Global Variable")
        smf.printf()

    # 3. show plugin
    elif target_show == "plugin":
        status_list = plugin.monitor()

        if not status_list:
            smf.printf(f"{CC.YELLOW}[!] No plugins available.{CC.RESET}")
            return

        # Header Tabel
        smf.printf()
        smf.printf(f"{CC.MAGENTA}{'-' * 36}{CC.RESET}")
        smf.printf(f"{CC.CYAN}{'PLUGIN NAME':<25} {'STATUS':<10}{CC.RESET}")
        smf.printf(f"{CC.MAGENTA}{'-' * 36}{CC.RESET}")
        smf.printf()

        for item in status_list:
            name = item["name"]
            status = item["status"]

            # Pewarnaan Status
            color = CC.WHITE
            if status == "ACTIVE":
                color = CC.GREEN
            elif status == "CRASHED":
                color = CC.RED
            elif status == "NON-ACTIVE":
                color = CC.YELLOW
            elif status == "ORPHANED":
                color = CC.BLUE

            smf.printf(f"{name:<25} {color}{status:<10}{CC.RESET}")

        smf.printf()

    elif target_show == "wordlist":
        word = utils.resolve_wordlist()

        if word:
            smf.printf()
            smf.printf(f"{CC.MAGENTA}{'-' * 30}{CC.RESET}")
            smf.printf(f"{CC.CYAN}{'Wordlist Collection':>15}{CC.RESET}")
            smf.printf(f"{CC.MAGENTA}{'-' * 30}{CC.RESET}")
            smf.printf()

            for w in word:
                smf.printf(f"  - {CC.YELLOW}{w}{CC.RESET}")
            smf.printf()
        else:
            smf.printf(f"{CC.YELLOW}[!] Wordlist not available.{CC.RESET}")

    # 5. show <category_name>
    else:
        module_files = utils.get_modules_in_category(target_show)

        if module_files:
            smf.printf()
            smf.printf(f"{CC.CYAN}Modules in {CC.RESET}({target_show}):")
            smf.printf()

            for mod in module_files:
                smf.printf(f"  - {CC.YELLOW}{mod}{CC.RESET}")
            smf.printf()
        else:
            smf.printf(
                f"{CC.YELLOW}[!] WARN => {CC.RESET}{target_show}{CC.YELLOW} > not found.{CC.RESET}"
            )
