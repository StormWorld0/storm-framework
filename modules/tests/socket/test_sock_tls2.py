import os
import smf
import ssl
import tempfile
import datetime

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
except ImportError:
    smf.printf("[*] Import Error cryptography.")


metadata = {
    "Name": "Testing TCP Socket TLS",
    "Description": """
Testing Socket TLS library python
""",
    "Author": ["zxelzy"],
    "Action": [["Scan", {"Description": "Testing socket"}]],
    "DefaultAction": "TLS",
    "License": "SMF License",
    "Date": "2026-09-17",
}
REQUIRED_OPTIONS = {"HOST": "", "PORT": ""}


def generate_cert():
    """Generate a self-signed TLS certificate with a non-RSA key."""
    key = ec.generate_private_key(ec.SECP256R1())
    sign_alg = hashes.SHA256()

    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "storm")])
    builder = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
    )
    cert = builder.sign(key, sign_alg)
    return key, cert


def _make_ssl_context(cert_path: str, key_path: str) -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.load_cert_chain(certfile=cert_path, keyfile=key_path)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    return ctx


def execute(options, net):
    host = options.get("HOST")
    port = options.get("PORT")

    data = (
        f"GET /anything HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: Storm-Framework/3.0\r\n"
        f"Accept: */*\r\n"
        f"Connection: Close\r\n"
        f"\r\n"
    ).encode("utf-8")

    key, cert = generate_cert()

    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )

    cert_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
    key_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
    try:
        cert_tmp.write(cert_pem)
        cert_tmp.close()
        key_tmp.write(key_pem)
        key_tmp.close()

        smf.printf(f"[*] Connecting (plain TCP) ...")
        sock = net.Socket()
        sock.create_connection((host, port))

        smf.printf("[*] Perform a TLS handshake using wrap_socket...")
        ssl_ctx = _make_ssl_context(cert_tmp.name, key_tmp.name)
        tls_sock = ssl_ctx.wrap_socket(
            sock,
            server_side=False,
            server_hostname=host,
            do_handshake_on_connect=False,
        )

        try:
            tls_sock.do_handshake()
        except ssl.SSLError as e:
            smf.printf("[!] TLS Handshake failed =>", e)
            return

        cipher = tls_sock.cipher()
        smf.printf(f"[+] TLS Handshake successful!")
        smf.printf(f"    Cipher: {cipher[0]} | Protocol: {cipher[1]}")
        smf.printf()

        smf.printf("[*] Sending data using TLS sendall!")
        tls_sock.settimeout(5)
        tls_sock.sendall(data)
        resp = tls_sock.recv(4096)
        if not resp:
            smf.printf("[!] Failed to perform TLS Recv!")
            return

        smf.printf("[✓] Raw Bytes =>", resp)
    except ssl.SSLError as e:
        smf.printf("[!] TLS Error =>", e)
    except ConnectionRefusedError as e:
        smf.printf("[!] Connection error =>", e)
    except OSError as e:
        smf.printf("[!] OS Error =>", e)
    finally:
        tls_sock.close()
        os.unlink(cert_tmp.name)
        os.unlink(key_tmp.name)
