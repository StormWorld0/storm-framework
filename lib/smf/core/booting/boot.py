# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import smf
import time
import sys
import os

from rootmap import ROOT

from apps.utility.verify import *
from apps.utility.spin import SpinBoot

from lib.roar.plugin_api import plugin
from lib.roar.cache import cache_modules as cache
from lib.roar.callbin import manager


def boot():
    smf.printd("Booting Storm Framework", level="INFO")

    try:
        with SpinBoot():
            # Check core startup security
            smf.printd("System synchronization is running", level="INFO")
            check_critical_files()

            # Plugin Daemon Service Manager
            smf.printd("Plugin daemon service is running", level="INFO")
            plugin.boot()

            # Cache modules synchronization
            smf.printd("Modules synchronization is running", level="INFO")
            cache.sync_modules()

            # Cache Binary synchronization
            smf.printd("Binary synchronization is running", level="INFO")
            manager.sync_bin()

            if not os.path.exists(os.path.join(ROOT, ".docker")):
                # Verify file integrity
                smf.printd("Integrity verification is running", level="INFO")
                run_verif()

        # Countdown to pause and start
        for i in range(5, 0, -1):
            sys.stdout.write(f"\r[✓] Successfully Starting Storm Framework [{i}]")
            sys.stdout.flush()
            time.sleep(1)

    except KeyboardInterrupt:
        smf.printf("\n[*] Booting successfully stopped.")
        sys.exit(2)
    except Exception as e:
        smf.printf(
            "[*] There was a failure while booting =>", e, file=sys.stderr, flush=True
        )
        smf.printd("Failed to boot Storm Framework", e, level="CRITICAL")
        sys.exit(1)
