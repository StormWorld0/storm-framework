import socket

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

    try:
        _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.printi("FD socket =>", _sock.fileno())

        sock = net.Socket()
        sock.socket(sock.AF_INET, sock.SOCK_STREAM, fileno=_sock.detach())
        log.prints("FD net.Socket =>", sock.fileno())

        sock.connect((host, port))

        resp = sock.sendall(b"abrakadabra")
        if not resp.ok:
            log.printw("Failed to send data =>", resp.message)
            return

        resp = sock.recv(1029)
        if not resp.ok:
            log.printw("Failed to receive data =>", resp.message)
            return

        log.prints("Int Bytes =>", resp.int_bytes)
        log.prints("Hex Bytes =>", resp.hex_bytes)
        log.prints("Raw Bytes =>", resp.raw_bytes)
    except Exception as e:
        log.printw("Error =>", e)
    finally:
        sock.close(sock.fileno())
    
