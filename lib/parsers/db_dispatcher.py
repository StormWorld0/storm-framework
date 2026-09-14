import os
import importlib
import subprocess
import threading
import tempfile
import smf

ADAPTER_PATH = "lib.parsers.adapters"
ADAPTER_DIR = os.path.join("lib", "parsers", "adapters")


def has_adapter(tool_name: str) -> bool:
    """Check if the specific adapter file (e.g. nmap.py) is available."""
    adapter_file = os.path.join(ADAPTER_DIR, f"{tool_name}.py")
    return os.path.exists(adapter_file)


def _background_ingest_task(adapter_module, target_tool: str, tmp_file: str):
    """A function that runs in the background to parse the output."""
    try:
        if not os.path.exists(tmp_file):
            return

        smf.printd(f"[*] Background parsing started for", target_tool, level="INFO")

        # Call the mandatory contract function from the adapter
        payloads = adapter_module.parse_to_payloads(tmp_file)

        # Import push_to_queue
        from lib.smf.ingest import push_to_queue

        count = 0
        for payload in payloads:
            push_to_queue(payload)
            count += 1

        smf.printd(f"{count} payloads from {target_tool} queued for DB!", level="SUCCESS")

    except Exception as e:
        smf.printd(f"DB Ingestion failed for {target_tool}", e, level="ERROR")
    finally:
        # Always clean up evidence
        if os.path.exists(tmp_file):
            os.remove(tmp_file)


def execute_tool(target_tool: str, original_args: list[str], cwd: str):
    """
    Execute the subprocess, block the REPL while running,
    then background parse after completion.
    """
    try:
        # Load module adapter dynamically
        adapter = importlib.import_module(f"{ADAPTER_PATH}.{target_tool}")

        # Create a secure temporary file
        fd, tmp_file = tempfile.mkstemp(prefix=f"smf_{target_tool}_")
        os.close(fd)

        # Ask the adapter to inject its secret arguments
        # Example: Nmap adapter will return ["nmap", "-sV", "-oX", "/tmp/xyz.xml"]
        injected_cmd = adapter.get_injection_args(tmp_file, original_args)

        smf.printd(f"Executing DB Wrapper: {' '.join(injected_cmd)}", level="INFO")
        smf.printf()  # Spasi kosong biar rapi

        # BLOCKING PHASE: Execute the original command
        # Let stdout spill naturally to the terminal screen
        process = subprocess.run(injected_cmd, cwd=cwd, check=False)

        if process.returncode == 0:
            # NON-BLOCKING PHASE: Parsing data in a separate thread
            t = threading.Thread(
                target=_background_ingest_task,
                args=(adapter, target_tool, tmp_file),
                daemon=True,
            )
            t.start()
        else:
            smf.printd(
                f"{target_tool} exited with error code {process.returncode}", level="WARN"
            )
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

    except KeyboardInterrupt:
        smf.printd(f"Execution aborted by user.", level="WARN")
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
    except Exception as e:
        smf.printd(f"Dispatcher failed for {target_tool}", e, level="ERROR")
    finally:
        smf.printf()
