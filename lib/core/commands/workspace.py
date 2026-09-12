import shlex
import smf

from apps.utility.colors import CC
from lib.smf.postgresql import (
    create_workspace,
    list_workspaces,
    Workspace,
    set_workspace,
    get_current_workspace,
    get_session,
)


def execute(args, ctx):
    """Handler untuk command 'workspace'.

    Usage:
        workspace               -> List semua workspace
        workspace add <name>    -> Tambah workspace
        workspace del <name>    -> Hapus workspace
        workspace <name>        -> Pindah workspace aktif
    """
    db = ctx.db
    if not db or not get_session():
        smf.printf(f"[!]{CC.YELLOW} No database connection active.{CC.RESET}")
        return

    raw_args = args if isinstance(args, str) else (" ".join(args) if args else "")
    parsed_args = shlex.split(raw_args) if raw_args else []
    current_ws_name = get_current_workspace()

    # Tanpa argumen -> List Workspace
    if not parsed_args:
        try:
            workspaces = list_workspaces()
            if not workspaces:
                return

            smf.printf(f"\n{CC.CYAN}Workspaces")
            smf.printf(f"{CC.MAGENTA}==========")
            smf.printf(f"{CC.GREEN}{'':<3} {'Name':<20} {'Hosts':<10}")
            smf.printf(f"{CC.MAGENTA}{'':<3} {'----':<20} {'-----':<10}")

            for ws in workspaces:
                active_marker = "*" if ws["name"] == current_ws_name else " "
                smf.printf(
                    f"{CC.YELLOW} {active_marker:<2} {ws['name']:<20} {ws['host_count']:<10}{CC.RESET}"
                )
            smf.printf("")
        except Exception as e:
            smf.printd("Failed to list workspaces", e, level="ERROR")
        return

    # Add Workspace (add <name>)
    if parsed_args[0] == "add" and len(parsed_args) > 1:
        target_name = " ".join(parsed_args[1:])
        res = create_workspace(target_name)
        if res:
            smf.printf(f"[+]{CC.GREEN} Added workspace =>{CC.RESET}", target_name)
        else:
            smf.printf(
                f"[-]{CC.YELLOW} Workspace =>{CC.RESET} {target_name} {CC.YELLOW}already exists{CC.RESET}"
            )

    # Delete Workspace (del <name>)
    elif parsed_args[0] == "del" and len(parsed_args) > 1:
        target_name = " ".join(parsed_args[1:])
        if target_name == "default":
            smf.printf(f"[-]{CC.YELLOW} Cannot delete the default workspace.{CC.RESET}")
            return

        # Hapus via ORM session dari db instance langsung
        try:
            ws = db.session.query(Workspace).filter_by(name=target_name).first()
            if ws:
                db.session.delete(ws)
                db.session.commit()
                smf.printf(f"[-]{CC.GREEN} Deleted workspace =>{CC.RESET}", target_name)

                if current_ws_name == target_name:
                    db.current_workspace = "default"
                    smf.printf(
                        f"[*]{CC.YELLOW} Switched back to workspace =>{CC.RESET} default"
                    )
            else:
                smf.printf(
                    f"[!] {CC.YELLOW}Workspace => {CC.RESET}{target_name}{CC.YELLOW} > not found.{CC.RESET}"
                )
        except Exception as e:
            db.session.rollback()
            smf.printd("Failed to delete workspace", e, level="ERROR")

    # Switch Workspace (<name>)
    else:
        target_name = parsed_args[0]
        ws = db.session.query(Workspace).filter_by(name=target_name).first()
        if ws:
            set_workspace(target_name)
            smf.printf(f"[*]{CC.YELLOW} Switched to workspace =>{CC.RESET}", target_name)
        else:
            smf.printf(
                f"[-]{CC.YELLOW} Workspace => {CC.RESET}{target_name}{CC.YELLOW} > not found.{CC.RESET}"
            )
