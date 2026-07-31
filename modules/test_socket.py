import socket
import ssl
import time

def create_tcp_socket(host: str, port: int, timeout: float = 5.0) -> socket.socket:
    """Membuka raw TCP socket biasa"""
    sock = socket.create_connection((host, port), timeout=timeout)
    return sock

def upgrade_socket_to_tls(sock: socket.socket, hostname: str = "127.0.0.1") -> ssl.SSLSocket:
    """Meng-upgrade socket TCP yang sedang terbuka menjadi TLS socket (Handshake)"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    tls_sock = ctx.wrap_socket(sock, server_hostname=hostname)
    return tls_sock

def send_and_receive(sock: socket.socket, data: bytes, read_size: int = 4096) -> tuple[int, bytes]:
    """Mengirim byte data dan membaca respon balik dari socket"""
    start = time.time()
    
    # Write
    sock.sendall(data)
    
    # Read
    try:
        response_data = sock.recv(read_size)
    except socket.timeout:
        response_data = b""
        
    rtt_ms = int((time.time() - start) * 1000)
    return rtt_ms, response_data


# =========================================================
# CARA PAKAI MODUL DI ATAS (Untuk Pengujian Ke Lab Server)
# =========================================================
if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 8443  # Port OpenSSL / Socat Test Server

    try:
        print("[1] Membuka Socket Raw TCP...")
        s = create_tcp_socket(HOST, PORT)
        print(f"    Type: {type(s).__name__}") # socket.socket

        print("\n[2] Meng-upgrade Socket ke TLS...")
        s = upgrade_socket_to_tls(s, hostname=HOST)
        print(f"    Type: {type(s).__name__}") # SSLSocket

        print("\n[3] Kirim Data via TLS Socket...")
        rtt, response = send_and_receive(s, b"PING TLS\n")
        print(f"    RTT: {rtt}ms | Response: {response}")

        s.close()
        print("\n[+] Test Selesai. Socket tertutup.")

    except Exception as e:
        print(f"\n[-] Error saat pengujian: {e}")
        
