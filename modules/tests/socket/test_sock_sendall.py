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


def execute(options, net, log):
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
        sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        log.printi("File Decriptor =>", sock.fileno())

        sock.connect((host, port))
        sock.sendall(data)

        resp = sock.recv(4096)
        if resp.ok:
            log.prints("Raw bytes =>", resp.raw_bytes)
            log.prints("Hex Bytes =>", resp.hex_bytes)
            log.prints("Int bytes =>", resp.int_bytes)
            log.prints("Str bytes =>", resp.str_bytes)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.printw("Error Socket =>", e)
    finally:
        sock.close(sock.fileno())
