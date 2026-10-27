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
REQUIRED_OPTIONS = {"HOST": "", "PORT": ""}


def execute(options, net):
    host = options.get("HOST")
    port = options.get("PORT")

    sock = net.Socket()
    try:
        smf.printf(f"[*] Getaddrinfo => {host}:{port}")
        resp = sock.getaddrinfo((host, port), af=sock.AF_INET, proto=sock.IPPROTO_TCP)
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
