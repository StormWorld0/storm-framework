# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import apps.utility.utils as utils

from apps.utility.colors import CC


# The set command is used to save data to global variables and module variables.
# it seems like the following example
# Command => set <var> <val>
# or
# Command => set ip 192.168.1.0
# a command like this will insert value data into the variable we implement.
def execute(args, ctx):
    options = ctx.options

    if len(args) >= 2:
        var_name = args[0].upper()
        var_value = args[1]

        if var_name not in options:
            smf.printf(
                f"{CC.YELLOW}[!] WARN =>{CC.RESET} {var_name} {CC.YELLOW}> is not a valid options!{CC.RESET}"
            )
            return

        allow = {"PASS", "WORD", "USER"}
        if var_name in allow:
            found_path = utils.resolve_path(var_value)

            if found_path:
                options[var_name] = found_path
                smf.printf(f"{CC.YELLOW}{var_name} => {found_path}{CC.RESET}")
            else:
                smf.printf(
                    f"{CC.YELLOW}[!] WARN =>{CC.RESET} {var_value} {CC.YELLOW}> not found!{CC.RESET}"
                )
        else:
            options[var_name] = var_value
            smf.printf(f"{CC.YELLOW}{var_name} => {var_value}{CC.RESET}")
    else:
        smf.printf(f"{CC.YELLOW}[!] Use the command =>{CC.RESET} set <VAR> <VALUE>")
