# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf

from apps.utility.colors import *
from lib.smfdb_helpers.log_utils import extract_logs
from lib.smfdb_helpers.log_stream import dump_log


# This command is used to retrieve specific logs that are stored.
# in the internal log database and differentiated using several log levels
# for example:
# (DEBUG, INFO, WARN, ERROR, CRITICAL)
#
# The commands that can be used are as follows!
#
# Command => log export debug
# Command => log export info
# and so forth.
# If the log is successfully retrieved, by default the resulting log file will be saved in HOME.
# or
# Command => log dump >> Dump all logs to terminal
# Will display all logs from the database to the terminal screen.
def execute(args, ctx):
    # Validate argument length.
    if len(args) <= 2:
        cmd = args[0].lower()
        
        if cmd == "export":
            val = args[1]
            valup = val.upper()
            
            # Security Validation (Whitelist)
            valid_levels = {"DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"}
            if valup not in valid_levels:
                smf.printf(
                    f"[!]{CC.YELLOW} Unknown log level => {valup} >> Allowed => {', '.join(valid_levels)}{CC.RESET}"
                )
                # Monitor user typos
                smf.printd("Invalid log extraction attempt", valup, level="WARN")
                return

            # Dynamic File Naming (Prevent Overwrite)
            # Example result: "log_info.txt"
            output_filename = f"log_{val}.txt"

            # Execute the extractor function with full parameters
            extract_logs(valup, output_file=output_filename)

        # Performing a log dump
        elif cmd == "dump":
            smf.printd("Performing a log dump", level="INFO")
            dump_log()

        else:
            # If the user types: take backup, take system, etc.
            smf.printf(
                f"[!] {CC.YELLOW}Unknown subcommand => {cmd} for >> export{CC.RESET}"
            )
    else:
        # If the user just types "log dump" or "log export" without a level argument
        smf.printf(f"[!]{CC.YELLOW} Argument failed. Usage: help{CC.RESET}")
        # Log syntax errors to the log database
        smf.printd("failed argument", args, level="WARN")
