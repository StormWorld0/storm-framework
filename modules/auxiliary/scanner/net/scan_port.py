import smf
import sys
from apps.utility.colors import C

STATUS_OPEN = "✅"
STATUS_CLOSED = "❌"

metadata = {
    "Name": "Publicly accessible port scanning",
    "Description": """
To scan public or local IPs to look for open ports
and look for specific ports that allow for testing
to find vulnerabilities, do a quick scan of.
""",
    "Author": ["zxelzy"],
    "Action": [["Scan", {"Description": "Searching for open ports"}]],
    "DefaultAction": "Scanner",
    "License": "SMF License",
    "Date": "2025-11-02",
}


def get_service_banner(target_ip, port, net):
    """
    Checking port status and parsing banner/version information via Go CRS Engine.
    """
    try:
        # Jika port HTTP, kita langsung titip payload 'HEAD /' di field Bod
        payload_body = ""
        if port in [80, 443, 8080]:
            payload_body = (
                f"HEAD / HTTP/1.1\r\nHost: {target_ip}\r\nConnection: close\r\n\r\n"
            )

        # Kirim argument sebagai dict/kwargs sesuai spec wrapper Python Anda
        s = net.Socket(
            host=target_ip,
            port=port,
            timeout=2.0,
        )
        if s.ok:
            r = s.send(data=payload_body, timeout=0.5)
        
        if r.ok:
            res = s.recv(1024)

        # Jika Go berhasil melakukan Dial (Socket Terbuka)
        if res.ok:
            status_color = f"{C.SUCCESS} OPEN " + STATUS_OPEN
            banner_info = "No version information."

            # Jika ada byte balasan/banner dari target
            if res.str_bytes:
                # Mengambil bytes UTF-8
                banner_str = res.str_bytes
                clean_banner = banner_str.strip()

                # Handling khusus Banner SSH (Port 22)
                if port == 22:
                    banner_info = clean_banner.split("\n")[0]

                # Handling khusus HTTP Server Header (Port 80, 443, 8080)
                elif port in [80, 443, 8080]:
                    server_header = next(
                        (
                            line
                            for line in clean_banner.split("\r\n")
                            if line.lower().startswith("server:")
                        ),
                        None,
                    )
                    if server_header:
                        # Ambil nilai misal "Server: nginx/1.18.0" -> "Server: nginx/1.18.0"
                        banner_info = server_header.strip()
                    else:
                        banner_info = "HTTP Response received."
                else:
                    # Port lain (FTP, SMTP, Redis, MySQL, dll) yang langsung menyapa
                    banner_info = clean_banner.split("\n")[0]

            return status_color, banner_info

        # Jika Go mengembalikan Error (Port Tertutup / Timeout)
        else:
            return f"{C.ERROR} CLOSED " + STATUS_CLOSED, None

    except KeyboardInterrupt:
        return
    except Exception as e:
        smf.printd("Global error service", e, level="ERROR")
        return f"{C.ERROR} ERROR ", None
    finally:
        s.close()


REQUIRED_OPTIONS = {"IP": ""}


def execute(options, net):
    """The main function is to run a scan with version/banner detection.."""

    target_ip = options.get("IP")

    port_names = {
        # === Remote & legacy ===
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        2323: "Alt Telnet",
        25: "SMTP",
        110: "POP3",
        143: "IMAP",
        # === DNS & Network ===
        53: "DNS",
        67: "DHCP",
        68: "DHCP",
        123: "NTP",
        161: "SNMP",
        389: "LDAP",
        5060: "UDP/TCP",
        5061: "TCP/TLS",
        10000: "RTP",
        20000: "RTP Atl",
        2000: "SCCP",
        16384: "VoIP",
        32767: "VoIP Alt",
        # === Web standard ===
        80: "HTTP",
        443: "HTTPS",
        3000: "NodeJS",
        5000: "Flask",
        5173: "Vite Dev",
        8000: "Django",
        8008: "HTTP Alt",
        8080: "HTTP Alt Proxy",
        8443: "HTTPS Alt",
        8888: "Dev Panel",
        # === Admin / panel vibes (🔥 sering juicy) ===
        81: "HTTP Alt",
        2082: "cPanel",
        2083: "cPanel SSL",
        2086: "WHM",
        2087: "WHM SSL",
        2095: "Webmail",
        2096: "Webmail SSL",
        # === Database ===
        1433: "MSSQL",
        1521: "Oracle",
        3306: "MySQL",
        5432: "PostgreSQL",
        6379: "Redis",
        27017: "MongoDB",
        # === File & storage ===
        139: "NetBIOS",
        445: "SMB",
        2049: "NFS",
        # === Java / Enterprise ===
        7001: "WebL",
        7002: "WebL SSL",
        8081: "HTTP Alt",
        9000: "PHP-FPM",
        9043: "WebSphere",
        # === Containers / DevOps ===
        2375: "Docker API",
        2376: "Docker API SSL",
        6443: "Kubernetes API",
        # === Monitoring ===
        9090: "Prometheus",
        9091: "Supervisor",
        9200: "Elasticsearch",
        5601: "Kibana",
    }
    ports_to_check = port_names.keys()

    smf.printf(f"{C.HEADER} SCANNING: PORT & VERSION in {target_ip}")
    MAX_TOTAL_WIDTH = 30
    try:
        for port in ports_to_check:
            status_line, banner = get_service_banner(target_ip, port, net)
            service_name = port_names.get(port, "Unknown Service")

            port_info_string = f"  Port {port} ({service_name})"
            padding_string = port_info_string.ljust(MAX_TOTAL_WIDTH)
            output_line = f"{C.MENU}{padding_string}: {status_line}"
            if "OPEN" in status_line:
                if (
                    banner
                    and "No information" not in banner
                    and "Error while retrieving banner" not in banner
                ):
                    clean_banner = banner.replace("\n", " ").strip()
                    output_line += f" {C.MENU} | {C.SUCCESS}{clean_banner}"
                else:
                    output_line += f" {C.MENU} | INFO: {banner}"

            output_line += f"{C.RESET}"
            smf.printf(output_line)

        smf.printf(f"{C.HEADER} --- SCAN COMPLETE ---")
    except KeyboardInterrupt:
        smf.printf(f"\n{C.ERROR}[!] Scan stopped.{C.RESET}")
        return
    except Exception as e:
        smf.printf(f"{C.ERROR}[!] ERROR =>", e, file=sys.stderr, flush=True)
        smf.printd("Global Exception", e, level="ERROR")
