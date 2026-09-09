import shlex
import smf

from apps.utility.colors import CC
from lib.smf.postgresql import get_services


def execute(args, ctx):
    """Handler untuk command 'services'.

    Usage:
        services           -> List semua service di workspace aktif
    """
    db = ctx.db
    if not db:
        smf.printf(f"[!]{CC.YELLOW} No database connection active.{CC.RESET}")
        return

    raw_args = args if isinstance(args, str) else (args[0] if args else "")
    parsed_args = shlex.split(raw_args) if raw_args else []

    current_ws = getattr(db, "current_workspace", "default")
    services_list = get_services(workspace_name=current_ws)

    if not services_list:
        smf.printf(f"[*]{CC.YELLOW} No services found in workspace: {CC.RESET}", current_ws)
        return

    smf.printf(f"\nServices ({current_ws})")
    smf.printf(f"============")
    smf.printf(f"{CC.GREEN}{'Host':<16} {'Port':<8} {'Proto':<8} {'Name':<15} {'State':<10} {'Info':<20}{CC.RESET}")
    smf.printf(f"{CC.MAGENTA}{'----':<16} {'----':<8} {'-----':<8} {'----':<15} {'-----':<10} {'----':<20}{CC.RESET}")

    for s in services_list:
        smf.printf(
            f"{CC.YELLOW}{s['host']:<16} {s['port']:<8} {s['proto']:<8} {s['name']:<15} {s['state']:<10} {s['info']:<20}{CC.RESET}"
        )
    smf.printf("")
