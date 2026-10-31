import smf

metadata = {
    "Name": "Testing TCP Socket Sendall",
    "Description": """
Testing Socket
""",
    "Author": ["zxelzy"],
    "Action": [["Scan", {"Description": "Testing socket"}]],
    "DefaultAction": "Post",
    "License": "SMF License",
    "Date": "2026-09-17",
}
REQUIRED_OPTIONS = {"HOST": "", "PORT": ""}


def execute(options, net):
    host = options.get("HOST")
    port = options.get("PORT")

    data = (
        f"POST /post HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: Storm-Framework/3.0\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: 32\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"HEX_BYTES_TEST_1234567890_ABCDEF"
    )

    sock = net.Socket()
    try:
        sock.settimeout(5.0)
        resp = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        if resp.ok:
            smf.printf("[✓] File Decriptor =>", sock.fileno())

        resp = sock.connect((host, port))
        if not resp.ok:
            smf.printf("[!] Failed connect =>", resp.message)
            return

        resp = sock.sendall(data)
        if not resp.ok:
            smf.printf("[!] Failed sendall =>", resp.message)
            return

        resp = sock.recv(4096)
        if resp.ok:
            smf.printf("[✓] Raw bytes =>", resp.raw_bytes)
            smf.printf("[✓] Hex Bytes =>", resp.hex_bytes)
            smf.printf("[✓] Int bytes =>", resp.int_bytes)
            smf.printf("[✓] Str bytes =>", resp.str_bytes)
    except KeyboardInterrupt:
        pass
    except sock.STrace as e:
        smf.printf("[*] Error Socket =>", e)
    finally:
        sock.close()
