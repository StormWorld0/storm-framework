import smf

metadata = {
    "Name": "Testing HTTP GET",
    "Description": """
Testing HTTPR GET
""",
    "Author": ["zxelzy"],
    "Action": [["Testing", {"Description": "Testing HTTP"}]],
    "DefaultAction": "Testing",
    "License": "SMF License",
    "Date": "2026-09-28",
}
REQUIRED_OPTIONS = {"URL": ""}


def execute(options, net):
    url = options.get("URL")
    http = net.HTTPR()
    try:
        http.timeout(10.0)
        http.setoptions(retry=2, verify=False)
        http.get(url)
        resp = http.run()

        if resp.ok:
            smf.printf("Server =>", resp.get_headers("server", "UNKNOWN"))
            smf.printf("Status =>", resp.status_code)
            smf.printf("Body   =>", resp.body[:1000])
    except http.HttpException as e:
        smf.printf("Error http requests =>", e)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        smf.printf("Error exception =>", e)
