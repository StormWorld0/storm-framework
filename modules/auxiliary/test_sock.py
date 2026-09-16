import smf

metadata = {
    "Name": "Publicly accessible port scanning",
    "Description": """
Testing Socket
""",
    "Author": ["zxelzy"],
    "Action": [["Scan", {"Description": "Testing socket"}]],
    "DefaultAction": "Scanner",
    "License": "SMF License",
    "Date": "2026-09-17",
}
REQUIRED_OPTIONS = {"IP": "", "PORT": ""}


def execute(options, net):
    ip = options.get("IP")
    port = options.get("PORT")

    sock = net.Socket.socket(AF_INET, SOCK_STREAM)
    try:
        if sock.ok:
            smf.printf(sock.fileno)

        sock.connect(ip, port)

        data = b"GET /anything HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"
        sock.send(data, timeout=1.0)

        if res := sock.recv(1024):
            smf.printf("String response =>", res.str_bytes)
            smf.printf("Raw response    =>", res.raw_bytes)
            smf.printf("Hex response    =>", res.hex_bytes)
            smf.printf("Int response    =>", res.read_bytes)
    except Exception as e:
        smf.printd("Socket testing failed", e, level="ERROR")
