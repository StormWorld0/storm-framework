import smf

from apps.utility.colors import CC
from lib.smf.postgresql import get_status

# Check the status of the database connection to PostgreSQL, to find out whether the framework is connected or not
# and all message statuses, workspaces, and database names will be displayed.
def execute(args, ctx):
    db = ctx.db
    if not db:
        smf.printf(f"[!]{CC.YELLOW} No database connection active.{CC.RESET}")
        return

    status_data = get_status()
    sts = status_data.get("status")
    rsn = status_data.get("reason")
    if sts == "connected":
        db_name = status_data.get("database", "")
        backend = status_data.get("backend", "")
        current_ws = getattr(db, "current_workspace", "")

        smf.printf(
            f"[*]{CC.YELLOW} Connected to ({CC.GREEN}{db_name}{CC.YELLOW}). Connection type:{CC.GREEN} {backend}. {CC.YELLOW}Workspace:{CC.GREEN} {current_ws}{CC.RESET}"
        )
    elif sts == "disconnected":
        smf.printf(
            f"[!]{CC.YELLOW} ({sts}) => {rsn}.{CC.RESET}"
        )
    else:
        smf.printf(f"[!]{CC.RED} ({sts}) => Failed to connect to database.{CC.RESET}")
