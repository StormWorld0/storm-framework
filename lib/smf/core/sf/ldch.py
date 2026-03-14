import os
from rootmap import ROOT


def session(options):
    full_path = os.path.join(ROOT, "lib", "smf", "cache", "res")
    cache_path = os.path.join(full_path, ".storm-session")
    # check cache files
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line:
                        # Split based on the first '=' sign found
                        key, value = line.split("=", 1)

                        # fill the variable according to the cache content
                        if key in options:
                            options[key] = value

            # delete cache file
            os.remove(cache_path)
            return options
        except Exception as e:
            print(f"[!] Error loading session: {e}")
            return options

    return options
