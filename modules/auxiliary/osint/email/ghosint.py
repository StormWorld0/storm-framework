import subprocess
import json
import os

from pathlib import Path
from rootmap import ROOT
from app.utility.colors import C

REQUIRED_OPTIONS = {
    "MODULE": "",
    "EMAIL": "",
}
def execute(options):
    module = options.get("MODULE")
    target = options.get("EMAIL")

    output_filename = "ghosint.json"
    base_path = Path(ROOT) / "script" / "ghunt"

    python_executable = base_path / "venv" / "bin" / "python"
    worker_script = base_path / "ghunt" / "ghunt.py"

    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_out_path = output_dir / output_filename

    try:
        check_ghunt = os.path.join(ROOT, "script", "ghunt", ".git")
        if os.path.exists(check_ghunt):
            payload = {
                "module": module,
                "target": target,
                "json_out": str(json_out_path),
            }
            process = subprocess.run(
                [str(python_executable), str(worker_script)],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                check=True,
            )
            return {"status": "success", "output": process.stdout}
        else:
            print(
                f"[*] Try running {C.SUCCESS}down ghosint{C.RESET} first to download the module."
            )

    except KeyboardInterrupt:
        return 
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}
