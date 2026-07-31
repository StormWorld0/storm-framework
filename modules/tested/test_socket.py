import smf

metadata = {
    # Unique Identification & Attribution Module
    "Name": "Testing Socket",
    "Description": """
To perform Engine socket testing in CRS
    """,
    "Author": ["zxelzy"],
    "License": "SMF LICENSE",
    "Date": "2026-07-31",
    "Action": [
        ["action name", {"Description": "brief explanation"}],
        ["action name", {"Description": "brief explanation"}],
    ],
    "DefaultAction": "Testing",
}

def execute(options, net):
    ip = "127.0.0.1"
    port = 8443

    smf.printf(f"[+] Initializing IPC Session to {ip}:{port}...")

    sock = net.Socket(host=ip, port=port, mode="duplex", infotls=True)

    try:
        # 2. Test TCP Send / Plaintext First
        smf.printf("\n[1] Sending Plaintext via TCP...")
        res_send = sock.send(data="PING_PLAINTEXT\n", mode="duplex")
        raw_send = res_send.get("data").get("raw_bytes")
        smf.printf(f"    Raw Response: {raw_send}")

        # 3. Test Upgrade TLS (Memanggil method uptls)
        smf.printf("\n[2] Upgrading Socket Session to TLS...")
        up = sock.uptls(cert="dummy_cert_str", key="dummy_key_str", verify=False)
        info = up.get("data").get("info_tls").get("tls_version")
        smf.printf(f"    TLS Info     : {info}")

        # 4. Test Send Data Terenkripsi di atas Session TLS yang Sama (Reused)
        smf.printf("\n[3] Sending Encrypted Data over Reused Session...")
        res_tls = sock.send(data="HELLO_TLS_ENCRYPTED\n", mode="duplex")
        raw = res_tls.get("data").get("raw_bytes")
        smf.printf(f"    Raw Response: {raw}")

    except Exception as e:
        smf.printf(f"\n[-] Error saat execution: {e}")
    finally:
        # 5. Cleanup Session di Engine Go
        smf.printf("\n[4] Closing Session...")
        sock.close()
