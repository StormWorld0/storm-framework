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
        sock.getaddrinfo(host, None, sproto=sock.IPPROTO_TCP)
    except sock.STrace as e:
        smf.printf("Error =>", e)
