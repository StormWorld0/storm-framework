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
        sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        log.printi("Socket created =>", sock.fileno())

        result = sock.connect((host, port))
        if not result.ok:
            log.printw("Connect failed =>", result.message)
            return

        log.printi("IP Local  =>", sock.getsockname())
        log.printi("IP Server =>", sock.getpeername())

        data = (
            f"GET /anything HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )

        result = sock.send(data)
        if not result.ok:
            log.printw("Send failed =>", result.message)
            return

        result = sock.recv(1024)
        if result.ok:
            log.prints("Int response    =>", result.int_bytes)
            log.prints("Hex response    =>", result.hex_bytes)
            log.prints("Raw response    =>", result.raw_bytes)
            log.prints("Str response    =>", result.str_bytes)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.printw("Socket testing failed =>", e)
    finally:
        sock.close(sock.fileno())
