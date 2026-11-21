import smf
import struct

metadata = {
    "Name": "Testing UDP Socket",
    "Description": """
Testing Socket
""",
    "Author": ["zxelzy"],
    "Action": [["Scan", {"Description": "Testing socket"}]],
    "DefaultAction": "Scanner",
    "License": "SMF License",
    "Date": "2026-09-17",
}
REQUIRED_OPTIONS = {"HOST": ""}


def build_dns_query(domain: str, txid: int = 0x1234) -> bytes:
    header = struct.pack(
        "!HHHHHH",
        txid,  # Transaction ID
        0x0100,  # Standard query + recursion desired
        1,  # QDCOUNT
        0,  # ANCOUNT
        0,  # NSCOUNT
        0,  # ARCOUNT
    )

    qname = b""

    for label in domain.split("."):
        encoded = label.encode("ascii")
        qname += bytes([len(encoded)]) + encoded

    qname += b"\x00"

    question = struct.pack(
        "!HH",
        1,  # QTYPE A
        1,  # QCLASS IN
    )
    return header + qname + question


def execute(options, net, log):
    host = options.get("HOST")
    port = 53
    sock = net.Socket()
    try:
        # Create a socket
        obj = sock.socket(sock.AF_INET, sock.SOCK_DGRAM, sock.IPPROTO_UDP)
        if not obj:
            return

        log.printi("File Decriptor =>", sock.fileno())

        # Connect to server
        result = sock.connect((host, port))
        if not result.ok:
            log.printw("DNS connect failed =>", result.message)
            return

        # Global timeout
        sock.settimeout(2.0)

        # Send data
        result = sock.sendall(build_dns_query(host))
        if not result.ok:
            log.printw("DNS query failed =>", result.message)
            return

        # Retrieve response Buffer
        result = sock.recv(4096)
        if result.ok:
            log.prints("Int Response       =>", result.int_bytes)
            log.prints("Raw Response       =>", result.raw_bytes)
            log.prints("Hex Response       =>", result.hex_bytes)
            log.prints("Str Response       =>", result.str_bytes)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.printw("UDP DNS testing failed =>", e)
    finally:
        sock.close(sock.fileno())
