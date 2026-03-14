import os
from rootmap import ROOT


def search_modules(query):
    # Langsung gunakan ROOT_DIR, tidak perlu os.path.dirname lagi di sini
    modules_path = os.path.join(ROOT, "modules")
    print(f"\n[*] Searching for: {query}")
    print(f"{'Module Path':<35} {'Category'}")
    print(f"{'-'*35} {'-'*15}")
    count = 0
    if not os.path.exists(modules_path):
        print(f"[-] Directory not found: {modules_path}")
        return
    for root, dirs, files in os.walk(modules_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_name_only = file.replace(".py", "").lower()

                if query.lower() in file_name_only:
                    count += 1
                    # rel_path tetap butuh modules_path agar hasilnya rapi (misal: network/ftp)
                    rel_path = os.path.relpath(os.path.join(root, file), modules_path)
                    clean_path = rel_path.replace(".py", "")
                    category = rel_path.split(os.sep)[0]

                    print(f"{clean_path:<35} {category}")

    if count == 0:
        print(f"[-] '{query}' Not found.")
        print("")
    else:
        print(f"\n[*] Found {count} module.")
        print("")
