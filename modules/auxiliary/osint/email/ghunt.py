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
    json = "storm-ghunt.json"
    # 1. Tentukan path ke Python di dalam venv GHunt
    # Sesuaikan 'script/ghunt/' dengan struktur folder aslimu
    base_path = os.path.join(ROOT, "script", "ghunt")

    # Jika Linux/Mac pakai 'bin'
    python_executable = base_path / "venv" / "bin" / "python"
    worker_script = base_path / "ghunt" / "ghunt.py"

    # 2. Siapkan data JSON untuk dikirim
    payload = {
        "module": module,
        "target": target,
        "json_out": str(Path(__file__).parent / "results" / json),
    }

    try:
        # 3. Panggil prosesnya
        # Kita pakai subprocess.run karena kamu mau "Selesai -> Mati"
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


# Contoh Penggunaan:
# result = call_ghunt_worker("email", "target@gmail.com", "target_info.json")
# print(result)
