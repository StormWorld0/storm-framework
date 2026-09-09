import smf

from apps.utility.colors import CC
from lib.smf.postgresql import get_status


def execute(args, ctx):
    db = ctx.db
    if not db:
        smf.printf(f"[!]{CC.YELLOW} No database connection active.{CC.RESET}")
        return

    status_data = get_status()
    if status_data and status_data.get("status") == "connected":
        db_name = status_data.get("database", "smf")
        backend = status_data.get("backend", "PostgreSQL")
        current_ws = getattr(db, "current_workspace", "default")

        smf.printf(
            f"[*]{CC.YELLOW} Connected to {db_name}. Connection type:{CC.GREEN} {backend}. {CC.YELLOW}Workspace:{CC.GREEN} {current_ws}{CC.RESET}"
        )
    else:
        smf.printf(f"[-]{CC.RED} Failed to connect to database.{CC.RESET}")
