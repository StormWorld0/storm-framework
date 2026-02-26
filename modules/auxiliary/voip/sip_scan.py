# MIT License.
# Copyright (c) 2026 Storm Framework

# See LICENSE file in the project root for full license information.


import socket

REQUIRED_OPTIONS = {"IP": "", "PORT": "standar port 5060"}


def execute(options):
    ip = options.get("IP")
    port = int(options.get("PORT"))
    payload = (
        f"OPTIONS sip:{ip} SIP/2.0\r\n"
        "Via: SIP/2.0/UDP 127.0.0.1:5060;branch=z9hG4bK-storm\r\n"
        "From: <sip:storm@storm-os>;tag=666\r\n"
        "To: <sip:target@target-ip>\r\n"
        "Call-ID: storm-scan-id\r\n"
        "CSeq: 1 OPTIONS\r\n"
        "Contact: <sip:storm@127.0.0.1>\r\n"
        "Max-Forwards: 70\r\n"
        "User-Agent: Storm-OS-VoIP-Scanner\r\n\r\n"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)
    try:
        sock.sendto(payload.encode(), (ip, port))
        data, addr = sock.recvfrom(2048)
        print(f"[+] Response from {addr}: {data.decode()}")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[-] No Response: {e}")
    finally:
        s.close()
