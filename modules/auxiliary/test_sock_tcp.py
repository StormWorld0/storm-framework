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
    ip = options.get("HOST")
    port = options.get("PORT")

    sock = net.Socket()

    try:
        result = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

        if result.ok:
            smf.printf("Socket created:", result.fileno)

        result = sock.connect(ip, port)

        if not result.ok:
            smf.printd("Connect failed", result, level="ERROR")
            return

        data = (
            b"GET /anything HTTP/1.1\r\n"
            b"Host: httpbin.org\r\n"
            b"Connection: close\r\n"
            b"\r\n"
        )

        result = sock.send(data, timeout=1.0)

        if not result.ok:
            smf.printd("Send failed", result, level="ERROR")
            return

        result = sock.recv(1024)

        if result.ok:
            smf.printf("String response =>", result.str_bytes)
            smf.printf("Raw response    =>", result.raw_bytes)
            smf.printf("Hex response    =>", result.hex_bytes)
            smf.printf("Int response    =>", result.read_bytes)
    except Exception as e:
        smf.printd("Socket testing failed", e, level="ERROR")
    finally:
        sock.close()
