import smf

from apps.utility.colors import CC
from lib.smf.postgresql import close_db


# Closes the database connection to PostgreSQL that is currently active in the background
# for security in database processes that are running in the background process
# and also to avoid exception errors from external libraries and internal libraries
# to cause data corruption in PostgreSQL.
def execute(args, ctx):
    resp = close_db()

    if resp is None:
        smf.printf(f"[!]{CC.YELLOW} There are no active database connections!{CC.RESET}")
    elif resp is False:
        smf.printf(f"[!]{CC.RED} Failed to close database connection!{CC.RESET}")
    else:
        smf.printf(f"[✓]{CC.GREEN} Successfully closed the database connection{CC.RESET}")
