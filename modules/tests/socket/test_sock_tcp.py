import smf

metadata = {
    "Name": "Testing TCP Socket",
    "Description": """
Testing Socket
""",
    "Author": ["zxelzy"],
    "Action": [["Scan", {"Description": "Testing socket"}]],
    "DefaultAction": "Scanner",
    "License": "SMF License",
    "Date": "2026-09-17",
}
REQUIRED_OPTIONS = {"HOST": "", "PORT": ""}


def execute(options, net):
    host = options.get("HOST")
    port = options.get("PORT")

    sock = net.Socket()
    try:
        result = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        if result.ok:
            smf.printf("Socket created:", sock.fileno())

        result = sock.connect(host, port)
        if not result.ok:
            smf.printd("Connect failed", result, level="ERROR")
            return

        smf.printf("IP Local  =>", sock.getsockname())
        smf.printf("IP Server =>", sock.getpeername())

        data = (
            f"GET /anything HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )

        sock.timeout(1.0)
        result = sock.send(data)

        if not result.ok:
            smf.printd("Send failed", result, level="ERROR")
            return

        result = sock.recv(1024)

        if result.ok:
            smf.printf("Int response    =>", result.int_bytes)
            smf.printf("Hex response    =>", result.hex_bytes)
            smf.printf("Raw response    =>", result.raw_bytes)
            smf.printf("Str response    =>", result.str_bytes)
    except KeyboardInterrupt:
        pass
    except sock.STrace as e:
        smf.printd("Socket testing failed", e, level="ERROR")
    finally:
        sock.close()
