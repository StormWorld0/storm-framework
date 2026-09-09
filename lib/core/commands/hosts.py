import shlex
import smf

from apps.utility.colors import CC
from lib.smf.postgresql import get_hosts


def execute(args, ctx):
    """Handler untuk command 'hosts'.

    Usage:
        hosts              -> List semua host di workspace aktif
    """
    db = ctx.db
    if not db:
        smf.printf(f"[!]{CC.YELLOW} No database connection active.{CC.RESET}")
        return

    raw_args = args if isinstance(args, str) else (args[0] if args else "")
    parsed_args = shlex.split(raw_args) if raw_args else []

    current_ws = getattr(db, "current_workspace", "default")
    hosts_list = get_hosts(workspace_name=current_ws)

    if not hosts_list:
        smf.printf(f"[*]{CC.YELLOW} No hosts found in workspace: {CC.RESET}", current_ws)
        return

    smf.printf(f"\nHosts ({current_ws})")
    smf.printf(f"==========")
    smf.printf(
        f"{CC.GREEN}{'Address':<16} {'MAC':<18} {'OS Name':<15} {'Purpose':<12} {'Info':<20}{CC.RESET}"
    )
    smf.printf(
        f"{CC.MAGENTA}{'-------':<16} {'---':<18} {'-------':<15} {'-------':<12} {'----':<20}{CC.RESET}"
    )

    for h in hosts_list:
        smf.printf(
            f"{CC.YELLOW}{h['address']:<16} {h['mac']:<18} {h['os_name']:<15} {h['purpose']:<12} {h['info']:<20}{CC.RESET}"
        )
    smf.printf("")
