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


def execute(options, net):
    ip = options.get("HOST")
    port = 53

    sock = net.Socket()

    try:
        # Create a socket
        result = sock.socket(sock.AF_INET, sock.SOCK_DGRAM, sock.IPPROTO_UDP)
        if not result.ok:
            smf.printd("Socket creation failed", result, level="ERROR")
            return

        smf.printf("File Decriptor =>", result.fileno)

        # Connect to server
        result = sock.connect(ip, port)
        if not result.ok:
            smf.printd("DNS connect failed", result, level="ERROR")
            return

        # Global timeout
        sock.timeout(2.0)

        # Build data
        query = build_dns_query("example.com")

        # Send data
        result = sock.send(query)
        if not result.ok:
            smf.printd("DNS query failed", result, level="ERROR")
            return

        # Retrieve response Buffer
        result = sock.recv(4096)
        if result.ok:
            smf.printf("Int Response       =>", result.int_bytes)
            smf.printf("Raw Response       =>", result.raw_bytes)
            smf.printf("Hex Response       =>", result.hex_bytes)

    except sock.STrace as e:
        smf.printd("UDP DNS testing failed", e, level="ERROR")
    finally:
        sock.close()
