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


def execute(options, net, log):
    host = options.get("HOST")
    port = options.get("PORT")

    sock = net.Socket()
    try:
        log.printi(f"Getaddrinfo => {host}:{port}")
        resp = sock.getaddrinfo((host, port), family=sock.AF_INET, proto=sock.IPPROTO_TCP)
        log.prints("Getaddrinfo Results =>", resp)

        addrs = [sockaddr for _, _, _, _, sockaddr in resp if sockaddr]

        if addrs is not None:
            log.printi()
            for addr in addrs:
                resp = sock.getnameinfo(addr)
                log.prints(f"Getnameinfo > {addr} =>", resp)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.printe("Error =>", e)
