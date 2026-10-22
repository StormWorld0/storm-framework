import os
import smf
from pathlib import Path


def get_home() -> Path:
    """
    Restores the original user home path.
    Avoid resolution to /root.
    """
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        try:
            import pwd

            return Path(pwd.getpwnam(sudo_user).pw_dir)
        except (KeyError, ImportError) as e:
            smf.printd("(KeyError, ImportError)", e, level="WARN")
    return Path.home()
