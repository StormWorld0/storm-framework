import shlex
import smf

from apps.utility.colors import CC
from lib.smf.postgresql import get_vulns, get_current_workspace

# This command will display all vulnerability data stored in the database.
# which is captured by the framework module or already exists will also be displayed
# structured with these commands.
def execute(args, ctx):
    """Handler for the 'vulns' command.
    Usage:
        vulns -> List all vulnerabilities in the active workspace
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
            f"[*]{CC.YELLOW} No vulnerabilities found in workspace =>{CC.RESET}",
            current_ws,
        )
        return

    smf.printf(f"\nVulnerabilities ({current_ws})")
    smf.printf(f"===============")
    smf.printf(
        f"{CC.GREEN}{'Host':<25} {'Port':<8} {'Proto':<8} {'Name':<25} {'Info'}{CC.RESET}"
    )
    smf.printf(
        f"{CC.MAGENTA}{'----':<25} {'----':<8} {'-----':<8} {'----':<25} {'----'}{CC.RESET}"
    )

    for v in vulns_list:
        smf.printf(
            f"{CC.YELLOW}{v['host']:<25} {v['port']:<8} {v['proto']:<8} {v['name']:<25} {v['info']}{CC.RESET}"
        )
    smf.printf("")
