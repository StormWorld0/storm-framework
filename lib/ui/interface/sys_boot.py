import readline  # noqa: F401
import sys

try:
    from lib.smf.core.booting.boot import *
    from ..banner import *
    from .start_interfc import *
except ImportError as e:
    smf.printf(f"Error import =>", e, file=sys.stderr)
    sys.exit(100)


def system_booting():
    boot()
    banner()
    main()
