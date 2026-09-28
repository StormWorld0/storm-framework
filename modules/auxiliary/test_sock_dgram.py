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
REQUIRED_OPTIONS = {"HOST": "", "PORT": ""}

dns_query = b"\xaa\xbb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01"


def execute(options, net):
    host = options.get("HOST")
    port = options.get("PORT")

    sock = net.Socket()

    try:
        # Socket Allocation
        resp = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
        if resp.ok:
            smf.printf("[*] File Descriptor =>", resp.fileno)

        # Global timeout
        sock.timeout(2.0)

        # Send datagram
        resp = sock.sendto(dns_query, host, port)
        if not resp.ok:
            smf.printf("[!] Failed sendto =>", resp.message)
            return

        # Get response Buffer and remote IP
        resp = sock.recvfrom(1024)
        if resp.ok:
            smf.printf("[✓] Remote IP    =>", resp.remote_ip)
            smf.printf()
            smf.printf("[✓] Raw Bytes    =>", resp.raw_bytes)
            smf.printf("[✓] Hex Bytes    =>", resp.hex_bytes)
            smf.printf("[✓] Int Bytes    =>", resp.int_bytes)
            smf.printf("[✓] Str Bytes    =>", resp.str_bytes)
            return

        smf.printf("[!] Failed recvfrom =>", resp.message)
    except Exception as e:
        smf.printd("Connection error", e, level="ERROR")
    finally:
        sock.close()
