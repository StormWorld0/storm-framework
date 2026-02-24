# MIT License.
# Copyright (c) 2026 Storm Framework

# See LICENSE file in the project root for full license information.


import os
import subprocess
import shutil
from rootmap import ROOT
from scripts.cpl.ioname import get_bin_name
from scripts.cpl.advcore import safe_mode
from concurrent.futures import ProcessPoolExecutor
# Merge all caches
SHARED_TARGET = os.path.join(ROOT, "lib", "smf", "core",  "cache", "rust_target")
def run_cmd(cmd, cwd=None):
    # Set environment variables
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
        print(f"[!] Rust Failed: {os.path.basename(cwd)}")
        return False


def compile_rust_project(cargo_path):
    output_dir = os.path.dirname(cargo_path)
    output_name = os.path.basename(os.path.abspath(output_dir))

    # Run as --offline
    # The --frozen flag ensures Cargo does not modify Cargo.lock
    # -j 1 This ensures 1 process uses 1 CPU core
    cmd = "cargo build --release --quiet --offline --frozen -j 1"

    if run_cmd(cmd, cwd=output_dir):
        bin_name = get_bin_name(cargo_path)
        src_bin = os.path.join(SHARED_TARGET, "release", bin_name)
        dst_bin = os.path.join(output_dir, output_name)

        if os.path.exists(src_bin):
            shutil.copy(shutil.which(src_bin) or src_bin, dst_bin)
            os.chmod(dst_bin, 0o755)
            return f"[✓] Rust: {output_name}"
    return f"[!] Rust Failed: {output_name}"

def compile_single_file(task):
    lang, src_path = task
    output = os.path.splitext(src_path)[0]

    if lang == "go":
        # Use -mod=vendor if you also vendor the Go libraries later.
        cmd = f"CGO_ENABLED=1 go build -o '{output}' '{src_path}'"
    else:
        with open(src_path, 'r', errors='ignore') as f:
            content = f.read()
        libs = "-lpcap" if "pcap.h" in content else ""
        cmd = f"gcc '{src_path}' -o '{output}' {libs}"

    if run_cmd(cmd):
        os.chmod(output, 0o755)
        return f"[✓] {lang.upper()}: {output}"
    return f"[!] {lang.upper()} Failed: {output}"

def main():
    os.chdir(ROOT)
    os.makedirs(SHARED_TARGET, exist_ok=True)

    rust_tasks = []
    other_tasks = []

    # SCANNING PHASE (Fast & Accurate)
    for root, dirs, files in os.walk("."):
        # Never enter a vendor or target!
        if any(x in root for x in [".git", "vendor", "cache", "target"]):
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

    if other_tasks and not os.path.exists("go.mod"):
        print("[*] Preparing Go Modules...")
        run_cmd("go mod init github.com/storm-os/storm-framework")
        run_cmd("go mod tidy")

    # EXECUTE PARALLEL
    print(f"[*] Storm Engine: Compiling on {os.cpu_count()} cores")
    with ProcessPoolExecutor(max_workers=safe_mode()) as executor:
        # Submit Rust projects
        rust_results = list(executor.map(compile_rust_project, rust_tasks))
        # Submit Go & C files
        other_results = list(executor.map(compile_single_file, other_tasks))

    for r in rust_results + other_results: print(r)

    # Delete the build_cache folder but after all the binaries have been moved
    # shutil.rmtree(os.path.join(ROOT, "cache"), ignore_errors=True)

if __name__ == "__main__":
    main()
