import smf
import time
import threading

metadata = {
    "Name": "Testing Listener Socket",
    "Description": """
Testing Socket Listener
""",
    "Author": ["zxelzy"],
    "Action": [["Scan", {"Description": "Testing socket"}]],
    "DefaultAction": "Testing",
    "License": "SMF License",
    "Date": "2026-09-28",
}


def execute(options, net):
    srv_sock = net.Socket()
    srv_sock.goroutine(5) # So that it doesn't block 2 active sockets
    clt_sock = None
    conn = None
    try:
        # Allocation
        resp = srv_sock.socket(srv_sock.AF_INET, srv_sock.SOCK_STREAM)
        if resp.ok:
            smf.printf("[*] Server Raw FD  =>", resp.fileno)

        # Allow Address Reuse (SO_REUSEADDR)
        srv_sock.setsockopt(srv_sock.SOL_SOCKET, srv_sock.SO_REUSEADDR, 1)

        # Bind ke Localhost port 0 (OS akan alokasikan Ephemeral Port acak)
        resp = srv_sock.bind("127.0.0.1", 0)
        if not resp.ok:
            smf.printf("[!] Bind Failed     =>", resp.message)
            return

        smf.printf("[✓] Bound to Address =>", resp.local_ip)

        # Parsing host dan port dinamis dari resp.local_ip ("127.0.0.1:PORT")
        host, port_str = resp.local_ip.rsplit(":", 1)
        port = int(port_str)

        # Listen dengan Backlog 5
        resp = srv_sock.listen(5)
        if not resp.ok:
            smf.printf("[!] Listen Failed   =>", resp.message)
            return
        smf.printf("[✓] Status Listen    => Success (Backlog: 5)")

        # Variable penampung ClientListener hasil accept()
        client_handler = []

        # Worker Thread untuk menjalankan accept()
        def accept_worker():
            # conn: ClientListener, acc_resp: ResponsePacket
            conn, resp = srv_sock.accept()
            client_handler.append((conn, resp))

        t = threading.Thread(target=accept_worker)
        t.daemon = True
        t.start()

        # Beri jeda 100ms agar thread server siap blocking di accept()
        time.sleep(0.1)

        # Client Simulator: Connect ke Port Ephemeral Server
        clt_sock = net.Socket()
        clt_sock.socket(clt_sock.AF_INET, clt_sock.SOCK_STREAM)
        resp = clt_sock.connect(host, port)

        if resp.ok:
            smf.printf("[✓] Client Connected =>", f"{host}:{port}")
        else:
            smf.printf("[!] Client Connect Failed =>", resp.message)
            return

        # Tunggu thread accept() menerima koneksi
        t.join(timeout=2.0)

        if not client_handler:
            smf.printf("[!] Accept Failed    => Timeout waiting for client")
            return

        conn, resp = client_handler[0]
        if not resp.ok:
            smf.printf("[!] Accept Error     =>", resp.message)
            return

        smf.printf(
            "[✓] Accepted Client  =>",
            f"{resp.remote_ip} (Client FD: {resp.fileno})",
        )

        # Echo Verification Test (PING - PONG)
        clt_sock.send(b"CLIENT_TEST_PING")

        # Server baca paket via ClientListener
        data = conn.recv(1024)
        smf.printf("[✓] Server Received  =>", data.raw_bytes)

        if data.raw_bytes == b"CLIENT_TEST_PING":
            # Server balas ke Client
            conn.send(b"SERVER_TEST_PONG")

            # Client terima balasan
            reply = clt_sock.recv(1024)
            smf.printf("[✓] Client Received  =>", reply.raw_bytes)
            smf.printf("\n[✓] SERVER LIFECYCLE TEST PASSED PERFECTLY!")
    except Exception as e:
        smf.printf("[!] Test Exception =>", e)
    finally:
        if conn is not None:
            conn.close()
        if srv_sock is not None:
            srv_sock.close()
        if clt_sock is not None:
            clt_sock.close()
