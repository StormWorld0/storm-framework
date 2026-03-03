# MIT License.
# Copyright (c) 2026 Storm Framework
# See LICENSE file in the project root for full license information.
import os
import subprocess
import shutil

from rootmap import ROOT
from app.utility.spin import StormSpin
from scripts.cpl.ioname import get_bin_name
from scripts.cpl.advcore import safe_mode
from concurrent.futures import ProcessPoolExecutor

SHARED_TARGET = os.path.join(ROOT, "lib", "smf", "core", "cache", "rust-session")

def run_cmd(cmd, cwd=None):
    env = os.environ.copy()
    env["CARGO_TARGET_DIR"] = SHARED_TARGET
    try:
        subprocess.run(
            cmd,
            shell=True,
            check=True,
            cwd=cwd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        print(f"[!] Rust Failed: {os.path.basename(cwd)}")
        return False

def compile_rust_project(cargo_path):
    output_dir = os.path.dirname(cargo_path)

    outdir = os.path.join(ROOT, "external", "source", "binary")
    bin_name = get_bin_name(cargo_path)

    src_bin = os.path.join(SHARED_TARGET, "release", bin_name)
    dst_bin = os.path.join(outdir, bin_name)

    if os.path.exists(src_bin):
        try:
            shutil.copy(src_bin, dst_bin)
            os.chmod(dst_bin, 0o755)
            return f"[✓] Rust: {bin_name}"
        except Exception as e:
            return f"[!] Copy Error: {bin_name} ({e})"

    return f"[!] Rust Binary Not Found: {bin_name}"



def compile_single_file(task):
    lang, src_path = task
    outdir = os.path.join(ROOT, "external", "source", "binary")
    bin_name = os.path.splitext(os.path.basename(src_path))[0]
    output = os.path.join(outdir, bin_name)

    if lang == "go":
        cmd = f"CGO_ENABLED=1 go build -o '{output}' '{src_path}'"
    else:
        with open(src_path, 'r', errors='ignore') as f:
            content = f.read()
        libs = "-lpcap" if "pcap.h" in content else ""
        cmd = f"gcc '{src_path}' -o '{output}' {libs}"

    if run_cmd(cmd):
        os.chmod(output, 0o755)
        return f"[✓] {lang.upper()}: {os.path.basename(output)}"
    return f"[!] {lang.upper()} Failed: {output}"



def main():
    os.chdir(ROOT)
    os.makedirs(SHARED_TARGET, exist_ok=True)

    rust_tasks = []
    other_tasks = []

    # SCANNING PHASE (Fast & Accurate)
    for root, dirs, files in os.walk("."):
        # ignore sensitive folders no compile
        if any(x in root for x in [".git", "db", "cache", "target", "binary"]):
            continue

        if "Cargo.toml" in files:
            rust_tasks.append(os.path.join(root, "Cargo.toml"))
            dirs[:] = []
            continue

        for file in files:
            full_path = os.path.join(root, file)
            if file.endswith(".go"):
                other_tasks.append(("go", full_path))
            elif file.endswith(".c"):
                other_tasks.append(("c", full_path))

    if rust_tasks:
        for cargo_path in rust_tasks:
            rust_dir = os.path.dirname(cargo_path)

            # Run heavy processes yourself with default logic
            with StormSpin():
                run_cmd("cargo build --release --offline", cwd=rust_dir)

    # Go.mod installation required by Golang compilation
    if other_tasks and not os.path.exists("go.mod"):
        print("[*] Preparing Go Modules...")
        run_cmd("go mod init github.com/STORM-CORP/storm-framework")
        run_cmd("go mod tidy")

    # Perform parallel compilation in all languages
    print(f"[*] Storm Engine: Compiling on {os.cpu_count()} cores")
    with ProcessPoolExecutor(max_workers=safe_mode()) as executor:
        rust_results_future = [executor.submit(compile_rust_project, task) for task in rust_tasks]
        other_results_future = [executor.submit(compile_single_file, task) for task in other_tasks]

        rust_results = [f.result() for f in rust_results_future]
        other_results = [f.result() for f in other_results_future]

if __name__ == "__main__":
    main()


