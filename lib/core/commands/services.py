import shlex
import smf

from apps.utility.colors import CC
from lib.smf.postgresql import get_services, get_current_workspace


# This command will display data that is currently stored as a service.
# in a PostgreSQL database table. Everything will look structured with this.
def execute(args, ctx):
    """Handler for the 'services' command.
    Usage:
        services -> List all services in the active workspace
    """
    db = ctx.db
    if not db:
        smf.printf(f"[!]{CC.YELLOW} No database connection active.{CC.RESET}")
        return

    current_ws = get_current_workspace()
    services_list = get_services(workspace_name=current_ws)

    if not services_list:
        smf.printf(
            f"[*]{CC.YELLOW} No services found in workspace =>{CC.RESET}", current_ws
        )
        return

    smf.printf(f"\nServices ({current_ws})")
    smf.printf(f"==================")
    smf.printf(
        f"{CC.GREEN}{'Host':<25} {'Port':<8} {'Proto':<8} {'Name':<18} {'State':<10} {'Info'}{CC.RESET}"
    )
    smf.printf(
        f"{CC.MAGENTA}{'----':<25} {'----':<8} {'-----':<8} {'----':<18} {'-----':<10} {'----'}{CC.RESET}"
    )

    for s in services_list:
        smf.printf(
            f"{CC.YELLOW}{s['host']:<25} {s['port']:<8} {s['proto']:<8} {s['name']:<18} {s['state']:<10} {s['info']}{CC.RESET}"
        )
    smf.printf("")
