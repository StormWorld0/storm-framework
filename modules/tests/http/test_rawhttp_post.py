import smf

metadata = {
    "Name": "Testing HTTP POST",
    "Description": """
Testing HTTPR RAW
""",
    "Author": ["zxelzy"],
    "Action": [["Scan", {"Description": "Testing HTTP"}]],
    "DefaultAction": "Testing",
    "License": "SMF License",
    "Date": "2026-09-28",
}
REQUIRED_OPTIONS = {"URL": ""}


def execute(options, net):
    url = options.get("URL")

    http = net.HTTPR()
    try:
        http.concurrency(50)
        http.timeout(10.0)
        http.setoptions(retry=2, verify=False)

        # Header & Raw Binary Body (mengandung NULL byte \x00 & non-printable bytes)
        headers = {"Content-Type": "application/octet-stream"}
        payload_bytes = b"\x00\x01\x02\xff\xfe\xfd_RAW_SOCKET_"

        # Tembak POST dengan Body Bytes
        http.rawhttp.post(url, headers=headers, body=payload_bytes)
        resp = http.run()

        if resp.ok:
            smf.printf("Server =>", resp.get_headers("server", "UNKNOWN"))
            smf.printf("Status =>", resp.status_code)
            smf.printf("Body   =>", resp.body[:1000])
    except http.HTrace as e:
        smf.printf("Error http requests =>", e)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        smf.printf("Error exception =>", e)
