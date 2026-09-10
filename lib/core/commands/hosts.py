import shlex
import smf

from apps.utility.colors import CC
from lib.smf.postgresql import get_hosts, get_current_workspace


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

    current_ws = get_current_workspace()
    hosts_list = get_hosts(workspace_name=current_ws)

    if not hosts_list:
        smf.printf(f"[*]{CC.YELLOW} No hosts found in workspace =>{CC.RESET}", current_ws)
        return

    smf.printf(f"\nHosts ({current_ws})")
    smf.printf(f"==================")
    smf.printf(
        f"{CC.GREEN}{'Address':<25} {'MAC':<25} {'OS Name':<18} {'Purpose':<12} {'Info'}{CC.RESET}"
    )
    smf.printf(
        f"{CC.MAGENTA}{'-------':<25} {'---':<25} {'-------':<18} {'-------':<12} {'----'}{CC.RESET}"
    )

    for h in hosts_list:
        smf.printf(
            f"{CC.YELLOW}{h['address']:<25} {h['mac']:<25} {h['os_name']:<18} {h['purpose']:<12} {h['info']}{CC.RESET}"
        )
    smf.printf("")
