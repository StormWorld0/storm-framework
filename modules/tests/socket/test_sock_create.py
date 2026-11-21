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


def execute(options, net, log):
    host = options.get("HOST")
    port = options.get("PORT")

    sock = net.Socket()
    try:
        res = sock.create_connection((host, port), timeout=2.0)
        if not res.ok:
            log.printw("Connect failed =>", res.message)
            return

        log.printi("Socket created =>", sock.fileno())
        log.printi("IP Local  =>", sock.getsockname())
        log.printi("IP Server =>", sock.getpeername())

        data = (
            f"GET /anything HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )

        sock.settimeout(1.0)
        res = sock.send(data)
        if not res.ok:
            log.printw("Send failed =>", res.message)
            return

        res = sock.recv(1024)
        if res.ok:
            log.prints("Int response    =>", res.int_bytes)
            log.prints("Hex response    =>", res.hex_bytes)
            log.prints("Raw response    =>", res.raw_bytes)
            log.prints("Str response    =>", res.str_bytes)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.printw("Socket testing failed =>", e)
    finally:
        sock.close(sock.fileno())
