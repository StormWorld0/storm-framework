import smf

metadata = {
    "Name": "Testing Cycle Socket",
    "Description": """
Testing Socket
""",
    "Author": ["zxelzy"],
    "Action": [["Scan", {"Description": "Testing socket"}]],
    "DefaultAction": "Testing",
    "License": "SMF License",
    "Date": "2026-09-28",
}
REQUIRED_OPTIONS = {"HOST": ""}


def execute(options, net):
    host = options.get("HOST")

    sock = net.Socket()

    try:
        resp = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        if resp.ok:
            smf.printf("[*] File Decriptor =>", resp.fileno)

        resp = sock.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
        if resp.ok:
            smf.printf("[✓] SetSockOpt executed successfully")

        resp = sock.bind(host, 0)
        sock.listen(1)
        if resp.ok:
            smf.printf("[*] Local Address =>", resp.local_ip)
    except Exception:
        smf.printd("Connection error", level="ERROR")
    finally:
        sock.close()
