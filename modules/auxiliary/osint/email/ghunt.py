import os
import subprocess
from pathlib import Path
from rootmap import ROOT

REQUIRED_OPTIONS = {
    "MODULE": "",
    "PORT": "",
}


def execute(options):

    module = options.get("MODULE")
    target = options.get("EMAIL")

    output_filename = "storm-ghunt.json"

    # 1. Tentukan path ke Python di dalam venv GHunt
    # Sesuaikan 'script/ghunt/' dengan struktur folder aslimu
    base_path = Path(ROOT) / "script" / "ghunt"

    # Jika Linux/Mac pakai 'bin'
    python_executable = base_path / "venv" / "bin" / "python"
    worker_script = base_path / "ghunt" / "ghunt.py"

    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_out_path = output_dir / output_filename

    # 2. Siapkan data JSON untuk dikirim
    payload = {
        "module": module,
        "target": target,
        "json_out": str(json_out_path),
    }

    try:
        process = subprocess.run(
            [str(python_executable), str(worker_script)],
            input=json.dumps(payload),  # Kirim JSON ke stdin
            text=True,
            capture_output=True,
            check=True,
        )

        return {"status": "success", "output": process.stdout}

    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}
