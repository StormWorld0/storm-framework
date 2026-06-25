# -- https://github.com/StormWorld0/storm-framework
# -- SMF License
import os
import importlib.util
import textwrap
import smf

from apps.utility.colors import *


# For those who like CVE collections, this logic is definitely needed
# Because this will produce output that is neat in structure and style.
# For ease of reading, and to differentiate between Description, name, ID, etc.
# The most important thing is to make sure that the CVE uses the example data format that has been provided.
# Otherwise the output will be messy and not according to storm rules.
def execute(args, ctx):
    query = args[0] if args else ""
    if not query:
        smf.printf(f"{CC.YELLOW}[!] Enter file name to info!{CC.RESET}")
        return

    # This is a special logic to know where the CVE is located.
    # Make sure CVE is always in the vulnerability folder
    vuln_path = "modules/"
    found_path = ""
    for root, dirs, files in os.walk(vuln_path):
        if f"{query}.py" in files:
            found_path = os.path.join(root, f"{query}.py")
            break

    if found_path:
        # To display information about a specific module
        # Command => info <modules_name>
        try:
            spec = importlib.util.spec_from_file_location("temp_mod", found_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # --- GET DICTIONARY MOD_INFO ---
            raw_info = getattr(mod, "metadata", {})
            info = {str(k).lower(): v for k, v in raw_info.items()}

            width = 80
            label_w = 13

            smf.printf()
            smf.printf(f"{CC.MAGENTA}{'='*width}{CC.RESET}")
            smf.printf(f"{CC.CYAN}{'STORM INFORMATION MODULES':^80}{CC.RESET}")
            smf.printf(f"{CC.MAGENTA}{'='*width}{CC.RESET}")

            # 1. BLOK WAJIB: Name, Description, Author, License
            mod_name = info.get("name", "UNTITLED MODULE")
            smf.printf(f"{CC.CYAN}{'Name':<{label_w}} : {CC.YELLOW}{mod_name}{CC.RESET}")

            smf.printf(f"{CC.CYAN}{'Description':<{label_w}}{CC.RESET}")
            raw_desc = info.get("description", "No description provided")
            desc = textwrap.fill(
                raw_desc.strip(),
                width=width - 2,
                initial_indent=" ",
                subsequent_indent=" ",
            )
            smf.printf(f"{CC.YELLOW}{desc}{CC.RESET}")
            smf.printf()

            # Menangani jika Author ditulis berupa List atau String murni
            authors = info.get("author", ["Unknown"])
            author_str = ", ".join(authors) if isinstance(authors, list) else str(authors)
            smf.printf(
                f"{CC.CYAN}{'Author':<{label_w}} : {CC.YELLOW}{author_str}{CC.RESET}"
            )

            mod_license = info.get("license", "SMF License")
            smf.printf(
                f"{CC.CYAN}{'License':<{label_w}} : {CC.YELLOW}{mod_license}{CC.RESET}"
            )

            mod_date = info.get("date", "N/A")
            smf.printf(f"{CC.CYAN}{'Date':<{label_w}} : {CC.WHITE}{mod_date}{CC.RESET}")
            smf.printf(f"{CC.MAGENTA}{'-'*width}{CC.RESET}")

            # 2. BLOK WAJIB: Action & Default Action
            smf.printf(f"{CC.CYAN}{'ACTION':<{label_w}}{CC.RESET}")
            actions = info.get("action", [])
            if actions and isinstance(actions, list):
                for action in actions:
                    # Antisipasi struktur invalid (bukan list-in-list [nama, dict])
                    if isinstance(action, (list, tuple)) and len(action) == 2:
                        act_name = action[0]
                        # Cari 'Description' atau 'description' di dalam inner-dict
                        act_dict = (
                            {str(k).lower(): v for k, v in action[1].items()}
                            if isinstance(action[1], dict)
                            else {}
                        )
                        act_desc = act_dict.get("description", "No action details")
                        smf.printf(
                            f"  > {CC.CYAN}{act_name:<9} : {CC.RESET}{CC.YELLOW}{act_desc}{CC.RESET}"
                        )
            else:
                smf.printf(f"  {CC.RED}[!] No executable actions defined{CC.RESET}")

            smf.printf()
            smf.printf(
                f"{CC.CYAN}{'DefAction':<{label_w}} : {CC.YELLOW}{info.get('defaultaction', 'Main')}{CC.RESET}"
            )

            # 3. BLOK DINAMIS: Vulnerability Intelligence (Kondisional)
            if "vulnerability" in info and info["vulnerability"]:
                vuln_data = info["vulnerability"]
                if isinstance(vuln_data, dict):
                    # Normalisasi sub-key internal vulnerability data
                    vuln_clean = {str(k).lower(): v for k, v in vuln_data.items()}

                    smf.printf(f"{CC.MAGENTA}{'-'*width}{CC.RESET}")
                    smf.printf(f"{CC.RED}{'VULNERABILITY INTELLIGENCE':^80}{CC.RESET}")
                    smf.printf(f"{CC.MAGENTA}{'-'*width}{CC.RESET}")

                    smf.printf(
                        f"  {CC.CYAN}- CVE       :{CC.RESET} {CC.YELLOW}{vuln_clean.get('cve', 'N/A')}{CC.RESET}"
                    )
                    smf.printf(
                        f"  {CC.CYAN}- Severity  :{CC.RESET} {CC.RED}{vuln_clean.get('severity', 'UNKNOWN')}{CC.RESET}"
                    )
                    smf.printf(
                        f"  {CC.CYAN}- Published :{CC.RESET} {CC.WHITE}{vuln_clean.get('published', 'N/A')}{CC.RESET}"
                    )
                    smf.printf(
                        f"  {CC.CYAN}- Updated   :{CC.RESET} {CC.WHITE}{vuln_clean.get('updated', 'N/A')}{CC.RESET}"
                    )

                    ref_links = vuln_clean.get("references", [])
                    if ref_links:
                        if isinstance(ref_links, list):
                            if len(ref_links) == 1:
                                smf.printf(
                                    f"  {CC.CYAN}- Reference :{CC.RESET} {CC.GREEN}{ref_links[0]}{CC.RESET}"
                                )
                            elif len(ref_links) > 1:
                                smf.printf(f"  {CC.CYAN}- Reference{CC.RESET}")
                                for link in ref_links:
                                    smf.printf(f"      {CC.GREEN}- {link}{CC.RESET}")
                        else:
                            smf.printf(
                                f"  {CC.CYAN}- Reference :{CC.RESET} {CC.GREEN}{ref_links}{CC.RESET}"
                            )

            # 4. BLOK DINAMIS: Transforms / Plugins (Kondisional)
            if "transforms" in info and info["transforms"]:
                trans_data = info["transforms"]
                if isinstance(trans_data, dict):
                    # Normalisasi sub-key internal transforms data
                    trans_clean = {str(k).lower(): v for k, v in trans_data.items()}

                    smf.printf(f"{CC.MAGENTA}{'-'*width}{CC.RESET}")
                    smf.printf(
                        f"{CC.YELLOW}{'PAYLOAD TRANSFORMS (PLUGIN MODE)':^80}{CC.RESET}"
                    )
                    smf.printf(f"{CC.MAGENTA}{'-'*width}{CC.RESET}")

                    for t_name, t_val in trans_clean.items():
                        # Berikan indikator warna khusus jika tipenya Boolean (Evasion Status)
                        if isinstance(t_val, bool):
                            status_color = CC.GREEN if t_val else CC.RED
                            smf.printf(
                                f"  * {t_name.upper():<13} : {status_color}{t_val}{CC.RESET}"
                            )
                        else:
                            smf.printf(f"  * {t_name.upper():<13} : {t_val}")

            smf.printf(f"{CC.MAGENTA}{'='*width}{CC.RESET}")
            smf.printf()

        except Exception as e:
            smf.printd("FAILED TO READ INFORMATION MODULE", e, level="ERROR")
            smf.printf(f"{CC.YELLOW}[!] Failed to read MODULE{CC.RESET}")
    else:
        smf.printf(f"{CC.YELLOW}[!] WARN => {query} > not found.{CC.RESET}")
