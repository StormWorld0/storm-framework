import smf

metadata = {
    "Name": "Testing HTTP POST",
    "Description": """
Testing HTTPR
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

        # Header & Body Teks
        headers = {"Content-Type": "text/plain"}
        payload_str = "testing"

        # Tembak POST dengan Body String
        http.post(url, headers=headers, body=payload_str)
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
