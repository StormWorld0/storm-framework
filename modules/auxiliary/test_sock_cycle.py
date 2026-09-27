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
    host = options.get("HOST", "127.0.0.1")

    sock = net.Socket()

    try:
        # Socket Allocation
        resp = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        if resp.ok:
            smf.printf("[*] File Descriptor =>", resp.fileno)
            return

        # Set SockOpt (SO_REUSEADDR)
        resp = sock.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
        if resp.ok:
            smf.printf("[✓] SetSockOpt executed successfully")

        # Bind to Host & Port 0 (Ephemeral)
        resp = sock.bind(host, 0)
        if resp.ok:
            smf.printf("[✓] Address & Port Local =>", resp.local_ip)
            return

        # Listen to make Server Socket
        resp = sock.listen(1)
        if resp.ok:
            smf.printf("[✓] Socket is now LISTENING")
        else:
            smf.printd(f"Listen failed", resp_listen.message, level="ERROR")

    except Exception as e:
        smf.printd("Connection error", e, level="ERROR")
    finally:
        sock.close()
