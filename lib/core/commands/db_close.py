import smf

from apps.utility.colors import CC
from lib.smf.postgresql import close_db

def execute(args, ctx):
    try:
        resp = close_db()

        if resp is None:
            smf.printf(f"[!]{CC.YELLOW} There are no active database connections!{CC.RESET}")
        elif resp is False:
            smf.printf(f"[!]{CC.RED} Failed to close database connection!{CC.RESET}")
        else:
            smf.printf(f"[✓]{CC.GREEN} Successfully closed the database connection{CC.RESET}")
