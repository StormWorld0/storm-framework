import os
from rootmap import ROOT


def session(options):
    full_path = os.path.join(ROOT, "lib", "smf", "cache")
    res_path = os.path.join(full_path, "res")

    os.makedirs(res_path, exist_ok=True)
    cache_path = os.path.join(res_path, ".storm-session")
    try:
        with open(cache_path, "w") as f:
            for key, value in options.items():
                # Save with KEY=VALUE format
                f.write(f"{key}={value}\n")
        return True
    except Exception as e:
        print(f"[!] Error saving session: {e}")
        return False
