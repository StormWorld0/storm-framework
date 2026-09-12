import smf
import re

from apps.utility.colors import CC
from lib.smf.postgresql import send_connect

# Attempting to connect to an active PostgreSQL
# to control the framework's internal data state storage and securely store it in a PostgreSQL database
# with this mechanism, we can connect to different PostgreSQL and it is free by default
# because the database connection is by default connected to the framework's default PostgreSQL.
def execute(args, ctx):
    if not args:
        smf.printf(
            f"[!]{CC.YELLOW} Use the format argument =>{CC.RESET} <user>:<pass>@<host>:<port>/<db>"
        )
        return

    data = args[0]

    pattern = re.compile(
        r"^(?P<user>[^:]+):"  # Match user up to the first ':' character
        r"(?P<pass>.*)@"  # Greedy match for passwords, ending with '@' at the end
        r"(?P<host>[^:@/]+):"  # Match host (IP/Domain) without delimiter
        r"(?P<port>\d+)/"  # Match port (numbers only)
        r"(?P<db>.+)$"  # The rest of the string is the database
    )

    match = pattern.match(data)
    if not match:
        smf.printf(f"[!]{CC.YELLOW} Invalid connection string format.{CC.RESET}")
        return

    raw = match.groupdict()
    connection_params = {
        "username": raw["user"],
        "password": raw["pass"],
        "host": raw["host"],
        "port": raw["port"],
        "database": raw["db"],
    }
    try:
        resp_dict = send_connect(connection_params)
        resp = resp_dict["status"]

        if resp == "success":
            smf.printf(f"[✓]{CC.GREEN} Connection successful!{CC.RESET}")
        elif resp == "warn":
            smf.printf(
                f"[!]{CC.YELLOW} There is something wrong with =>{CC.RESET} Pass, User, Host, Port, DB{CC.YELLOW} > Make sure the data is correct.{CC.RESET}"
            )
        else:
            smf.printf(f"[*]{CC.RED} Invalid connection!{CC.RESET}")
    except Exception as e:
        smf.printd("Failed to send connect", e, level="ERROR")
