import smf
from apps.utility.colors import CC


def execute(args, ctx):
    db = ctx.db

    if not db or not getattr(db, "session", None):
        smf.printf("[-] No database connection active.")
        return

    try:
        # Test queries directly to the Postgres driver via ORM
        db.session.execute("SELECT 1")
        db_name = getattr(db, "db_name", "smf")
        current_ws = getattr(db, "current_workspace", "default")
        smf.printf(
            f"[*]{CC.YELLOW} Connected to {db_name}. Connection type:{CC.GREEN} PostgreSQL. {CC.YELLOW}Workspace:{CC.GREEN} {current_ws}{CC.RESET}"
        )
    except Exception as e:
        smf.printd("Database connection error", e, level="ERROR")
