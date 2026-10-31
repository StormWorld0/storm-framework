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
        res = sock.create_connection((host, port), timeout=2.0)
        if not res.ok:
            smf.printd("Connect failed", res, level="ERROR")
            return

        smf.printf("Socket created =>", sock.fileno())
        smf.printf("IP Local  =>", sock.getsockname())
        smf.printf("IP Server =>", sock.getpeername())

        data = (
            f"GET /anything HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )

        sock.settimeout(1.0)
        res = sock.send(data)
        if not res.ok:
            smf.printd("Send failed", res, level="ERROR")
            return

        res = sock.recv(1024)
        if res.ok:
            smf.printf("Int response    =>", res.int_bytes)
            smf.printf("Hex response    =>", res.hex_bytes)
            smf.printf("Raw response    =>", res.raw_bytes)
            smf.printf("Str response    =>", res.str_bytes)
    except KeyboardInterrupt:
        pass
    except sock.STrace as e:
        smf.printd("Socket testing failed", e, level="ERROR")
    finally:
        sock.close()
