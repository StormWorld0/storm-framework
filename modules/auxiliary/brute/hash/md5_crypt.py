import crypt
from app.utility.colors import C

REQUIRED_OPTIONS = {"HASH": "", "PASS": ""}


def execute(options):
    """
    Cracking MD5-Crypt password hashes using wordlists.
    """
    shadow_entry = options.get("HASH")
    wordlist_file = options.get("PASS")

    try:
        parts = shadow_entry.split(":")
        if len(parts) < 2:
            print(f"{C.ERROR} Input at least (user:hash...)")
            return

        username = parts[0]
        full_hash = parts[1]

        # Salt Extraction for MD5-Crypt ($1$)
        if full_hash.startswith("$1$"):
            # Ensure the MD5-Crypt structure has 3 parts: $1$salt$hash_value
            salt_parts = full_hash.split("$")
            if len(salt_parts) < 3:
                print(f"{C.ERROR} Incomplete MD5-Crypt hash structure.")
                return

            salt_crypt = f"${salt_parts[1]}${salt_parts[2]}"  # Format: $1$t7y583it
        else:
            print(f"{C.ERROR} Unsupported hash format (Not MD5-Crypt $1$).")
            return
    except Exception as e:
        print(f"{C.ERROR} Hash parsing error: {e}")
        return

    print(f"{C.MENU} --- PYTHON SHADOW CRACKER (MD5-Crypt) ---")
    print(f"{C.MENU} [*] Target User: {username}")
    print(f"{C.MENU} [*] Hash Type: MD5-Crypt ($1$)")
    print(f"{C.MENU} [*] Salt: {salt_crypt}")
    print(f"{C.MENU} [*] Loading Wordlist from: {wordlist_file}")

    try:
        with open(wordlist_file, "r", encoding="latin-1") as f:
            for line in f:
                word = line.strip()
                if not word:
                    continue

                hashed_word = crypt.crypt(word, salt_crypt)
                print(f"{C.MENU}  Try: {word}{C.RESET}", end="\r")

                if hashed_word == full_hash:
                    print(f"{C.SUCCESS} [✓] SUCCESSFULLY FOUND U:{username} H:{word}")
                    print(
                        f"{C.SUCCESS} --------------------------------------------------"
                    )
                    return

        print(f"{C.ERROR} \n[-] Failed to find password in wordlist.")

    except KeyboardInterrupt:
        return
    except FileNotFoundError:
        print(f"{C.ERROR} \n[-] ERROR: Wordlist file not found.")
    except Exception as e:
        print(f"{C.ERROR} \n[-] Unexpected error while cracking: {e}")
        return
