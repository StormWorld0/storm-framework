import smf

from apps.utility.colors import CC
from lib.smf.postgresql import get_cerds, get_current_workspace


# This command displays a list of credentials stored in the database
# and will be displayed in a structured manner with this.
def execute(args, ctx):
    """Handler for the 'creds' command.
    Usage:
        services -> List all credential in the active workspace
    """
    db = ctx.db
    if not db:
        smf.printf(f"[!]{CC.YELLOW} No database connection active.{CC.RESET}")
        return

    current_ws = get_current_workspace()
    cerds_list = get_cerds(workspace_name=current_ws)

    if not cerds_list:
        smf.printf(
            f"[*]{CC.YELLOW} No credential found in workspace =>{CC.RESET}", current_ws
        )
        return

    smf.printf(f"\nCredential ({current_ws})")
    smf.printf(f"==================")
    smf.printf(
        f"{CC.GREEN}{'Address':<25} {'Host':<25} {'Port':<8} {'Public':<18} {'Private':<18} {'Type':<12} {'Realm':<18} {'Created':<12} {'Status':<10} {'Level':<8}{CC.RESET}"
    )
    smf.printf(
        f"{CC.MAGENTA}{'----':<25} {'----':<25} {'----':<8} {'------':<18} {'-------':<18} {'----':<12} {'-----':<18} {'-------':<12} {'------':<10} {'-----':<8}{CC.RESET}"
    )

    for s in cerds_list:
        smf.printf(
            f"{CC.YELLOW}{s['addr']:<25} {s['host']:<25} {s['port']:<8} {s['public']:<18} {s['private']:<18} {s['type']:<12} {s['realm']:<18} {s['created']:<12} {s['status']:<10} {s['level']:<8}{CC.RESET}"
        )
    smf.printf("")
