# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import sys
import time
import threading
from pathlib import Path
from apps.utility.verify import check_critical_files
from apps.utility.spin import SpinBoot
from lib.roar.crs import CRSD
from lib.roar.plugin_api import plugin
from lib.roar.cache import cache_modules as cache
from lib.roar.callbin.manager import BinaryManager
from lib.smf.postgresql import DBManager
from lib.smf.exception.handler import exception_handler


def sysboot():
    smf.printd("Booting Storm Framework", level="INFO")
    sys.excepthook = exception_handler
    threading.excepthook = lambda args: exception_handler(
        args.exc_type, args.exc_value, args.exc_traceback
    )
    try:
        with SpinBoot():
            # Check core startup security
            smf.printd("System synchronization is running", level="INFO")
            check_critical_files()

            # Cache Binary synchronization
            if not BinaryManager().sync_bin():
                smf.printd("Failed to synchronize Binary", level="ERROR")
                raise

            # Connection Runtime Service Daemon
            if not CRSD._turn_on_process():
                smf.printd(
                    "Failed to start Connection Runtime Service Daemon", level="WARN"
                )

            # Plugin Daemon Service Manager
            if not plugin.boot():
                smf.printd("Failed to activate Plugin Service", level="WARN")

            # Cache modules synchronization
            if not cache.sync_modules():
                smf.printd("Failed to synchronize Modules", level="WARN")

            # Enabling PostgreSQL workspace database runtime
            if (config_path := Path.home() / ".smf" / "database.yml").exists():
                db = DBManager(config_path)
                db.current_workspace = "default"

            # Countdown to pause and start
            time.sleep(2)
    except KeyboardInterrupt:
        smf.printf("\n[*] Booting successfully stopped.")
        sys.exit(2)
    except Exception as e:
        smf.printf(
            "[*] There was a failure while booting =>", e, file=sys.stderr, flush=True
        )
        smf.printd("Failed to boot Storm Framework", e, level="CRITICAL")
        sys.exit(1)
