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

    sock = net.Socket(host=ip, port=port, mode="duplex")

    try:
        # 2. Test TCP Send / Plaintext First
        smf.printf("\n[1] Sending Plaintext via TCP...")
        sock.send(data="PING_PLAINTEXT\n", timeout=10)

        res_send = sock.recv(24)
        rep = res_send.get("status")
        if rep == "SUCCESS":
            raw_send = res_send.get("data").get("raw_bytes")
            smf.printf(f"    Raw Response: {raw_send}")

        # 3. Test Upgrade TLS (Memanggil method uptls)
        smf.printf("\n[2] Upgrading Socket Session to TLS...")
        up = sock.uptls(cert="", key="", verify=False)
        
        res = up.get("status")
        if res == "SUCCESS":
            info = up.get("tls_version")
            smf.printf(f"    TLS Info     : {info}")

        # 4. Test Send Data Terenkripsi di atas Session TLS yang Sama (Reused)
        smf.printf("\n[3] Sending Encrypted Data over Reused Session...")
        sock.send(data="HELLO_TLS_ENCRYPTED\n", timeout=10)

        res_tls = sock.recv(24)
        st = res_tls.get("status")
        if st == "SUCCESS":
            raw = res_tls.get("data").get("raw_bytes")
            smf.printf(f"    Raw Response: {raw}")

    except Exception as e:
        smf.printf(f"\n[-] Error saat execution: {e}")
    finally:
        # 5. Cleanup Session di Engine Go
        smf.printf("\n[4] Closing Session...")
        sock.close()
