import smf
import tempfile

from datetime import datetime, timedelta, timezone
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

metadata = {
    "Name": "Testing TCP Socket Sendall",
    "Description": """
Testing Socket
""",
    "Author": ["zxelzy"],
    "Action": [["Scan", {"Description": "Testing socket"}]],
    "DefaultAction": "Post",
    "License": "SMF License",
    "Date": "2026-09-17",
}
REQUIRED_OPTIONS = {"HOST": "", "PORT": ""}

def generate_temp_tls_files(target_dir, common_name="localhost"):
    cert_path = os.path.join(target_dir, "temp_server.crt")
    key_path = os.path.join(target_dir, "temp_server.key")

    # 1. Generate Private Key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. Build Certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(common_name)]),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )

    # 3. Write Key & Cert ke Temp Folder
    with open(key_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    return cert_path, key_path
    

def execute(options, net):
    host = options.get("HOST")
    port = options.get("PORT")

    data = (
        f"GET /get HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: Storm-Framework/3.0\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"HEX_BYTES_TEST_1234567890_ABCDEF"
    )

    sock = net.Socket()
    try:
        sock.timeout(5.0)
        resp = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        if resp.ok:
            smf.printf("[✓] File Decriptor =>", resp.fileno)
            
        resp = sock.connect(host, port)
        if not resp.ok:
            smf.printf("[!] Failed connect =>", resp.message)
            return

        with tempfile.TemporaryDirectory() as tmp_dir:
            cert_file, key_file = generate_temp_tls_files(tmp_dir, common_name=host)

            resp = sock.uptls(cert_file, key_file, verify=False)
            if not resp.ok:
                smf.printf("[!] Failed Upgrade TLS =>", resp.message)
                return

            smf.printf("[✓] Cipher     =>", resp.tls.cipher_suite)
            smf.printf("[✓] Version    =>", resp.tls.version)
            smf.printf("[✓] Protocol   =>", resp.tls.protocol)
            smf.printf("[✓] Handshake  =>", resp.tls.handshake)
            smf.printf()

            resp = sock.send(data)
            if not resp.ok:
                smf.printf("[!] Failed Send TLS =>", resp.message)
                return
            
            resp = sock.recv(1024)
            if not resp.ok:
                smf.printf("[!] Failed Recv TLS =>", resp.message)
    except sock.STrace as e:
        smf.printf("[*] Error Socket =>", e)
    finally:
        sock.close()

