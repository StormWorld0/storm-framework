import smf

metadata = {
    "Name": "Testing Getaddrinfo Socket",
    "Description": """
Testing Socket
""",
    "Author": ["zxelzy"],
    "Action": [["Scan", {"Description": "Testing socket"}]],
    "DefaultAction": "Testing",
    "License": "SMF License",
    "Date": "2026-09-28",
}
REQUIRED_OPTIONS = {"HOST": ""}


def execute(options, net):
    host = options.get("HOST")

    sock = net.Socket()
    try:
        smf.printf("[*] Getaddrinfo =>", host)
        resp = sock.getaddrinfo(host, None, addrf=sock.AF_INET, sproto=sock.IPPROTO_TCP)
        smf.printf("[✓] Getaddrinfo Results =>", resp)

        addrs = [sockaddr for _, _, _, _, sockaddr in resp if sockaddr]

        if addrs is not None:
            smf.printf()
            for addr in addrs:
                resp = sock.getnameinfo(addr)
                smf.printf(f"[✓] Getnameinfo > {addr} =>", resp)
    except KeyboardInterrupt:
        pass
    except sock.STrace as e:
        smf.printf("Error =>", e)
