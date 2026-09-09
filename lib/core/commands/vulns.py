import shlex
import smf

from apps.utility.colors import CC
from lib.smf.postgresql import get_vulns, get_current_workspace


def execute(args, ctx):
    """Handler untuk command 'vulns'.

    Usage:
        vulns              -> List semua vulnerability di workspace aktif
    """
    db = ctx.db
    if not db:
        smf.printf(f"[!]{CC.YELLOW} No database connection active.{CC.RESET}")
        return

    raw_args = args if isinstance(args, str) else (args[0] if args else "")
    parsed_args = shlex.split(raw_args) if raw_args else []

    current_ws = get_current_workspace()
    vulns_list = get_vulns(workspace_name=current_ws)

    if not vulns_list:
        smf.printf(
            f"[*]{CC.YELLOW} No vulnerabilities found in workspace: {CC.RESET}",
            current_ws,
        )
        return

    smf.printf(f"\nVulnerabilities ({current_ws})")
    smf.printf(f"===============")
    smf.printf(
        f"{CC.GREEN}{'Host':<16} {'Port':<8} {'Proto':<8} {'Name':<25} {'Info':<25}{CC.RESET}"
    )
    smf.printf(
        f"{CC.MAGENTA}{'----':<16} {'----':<8} {'-----':<8} {'----':<25} {'----':<25}{CC.RESET}"
    )

    for v in vulns_list:
        smf.printf(
            f"{CC.YELLOW}{v['host']:<16} {v['port']:<8} {v['proto']:<8} {v['name']:<25} {v['info']:<25}{CC.RESET}"
        )
    smf.printf("")
