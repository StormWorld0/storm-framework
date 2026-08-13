import smf
import os

from apps.utility.colors import *

from rootmap import ROOT
from pathlib import Path


def cleaner() -> None:
    root = os.path.join(ROOT, "lib", "smf", "core")
    path = os.path.join(root, "sf", "cache", "integrity", "injection.state")

    state_file = Path(path).resolve()
    root_dir = Path(ROOT).resolve()

    if not state_file.is_file():
        smf.printf("[*] Storm Framework is verified safe")
        return

    # Reading state file
    with open(state_file, "r", encoding="utf-8") as f:
        targets = [line.strip() for line in f if line.strip()]

    # Scan path Injection
    for raw_path in targets:
        # Heading to the precision location
        target_path = (root_dir / raw_path).resolve()

        # Security Mitigation: Preventing Path Traversal
        if not target_path.is_relative_to(root_dir):
            smf.printf(
                f"[{CC.YELLOW}ALERT{CC.RESET}]{CC.CYAN} Path is ignored{CC.RESET} =>",
                raw_path,
            )
            continue

        # Direct Lookup & Delete Ops (FILE ONLY)
        try:
            if target_path.is_file():
                target_path.unlink()  # Deleting files
                smf.printf(f"[{CC.GREEN}FOUND & DELETE{CC.RESET}] =>", raw_path)
            else:
                smf.printf(f"[{CC.YELLOW}FILE NOT FOUND{CC.RESET}] =>", raw_path)
        except OSError as e:
            smf.printf(f"[{CC.RED}ERROR DELETING{CC.RESET}] => {raw_path} >", e)
            smf.printd(f"Deleting failed: {raw_path}", e, level="WARN")

    # Task completed: Destroy the injection.state file
    try:
        state_file.unlink()
        smf.printf(
            f"\n[{CC.GREEN}DONE{CC.RESET}]{CC.CYAN} Cleaning is complete{CC.RESET}"
        )
    except OSError as e:
        smf.printf(f"\n[*] Failed to delete file {state_file.name} =>", e)
        smf.printd(f"Failed to delete file {state_file.name}", e, level="ERROR")


if __name__ == "__main__":
    cleaner()
