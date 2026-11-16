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


def execute(options, net, log):
    srv_sock = net.Socket()
    clt_sock = None
    conn = None
    try:
        # Allocation
        srv_sock.socket(srv_sock.AF_INET, srv_sock.SOCK_STREAM)
        log.printi("Server RawFD  =>", srv_sock.fileno())

        # Allow Address Reuse (SO_REUSEADDR)
        srv_sock.setsockopt(srv_sock.SOL_SOCKET, srv_sock.SO_REUSEADDR, 1)

        # Bind ke Localhost port 0 (OS akan alokasikan Ephemeral Port acak)
        resp = srv_sock.bind(("127.0.0.1", 0))
        if not resp.ok:
            log.printw("Bind Failed     =>", resp.message)
            return

        host, port = srv_sock.getsockname()

        log.printi("Bound to Address =>", f"{host}:{port}")

        # Listen dengan Backlog 5
        resp = srv_sock.listen(5)
        if not resp.ok:
            log.printw("Listen Failed   =>", resp.message)
            return
        log.printi("Status Listen    => Success (Backlog: 5)")

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
        if clt_sock:
            log.prints("Socket ClientFD =>", clt_sock.fileno())

        resp = clt_sock.connect((host, port))

        if resp.ok:
            log.prints("Client Connected =>", f"{host}:{port}")
        else:
            log.printw("Client Connect Failed =>", resp.message)
            return

        # Tunggu thread accept() menerima koneksi
        t.join(timeout=2.0)

        if not client_handler:
            log.printw("Accept Failed    => Timeout waiting for client")
            return

        conn, resp = client_handler[0]
        if not resp.ok:
            log.printw("Accept Error     =>", resp.message)
            return

        log.prints("Accepted ClientFD =>", conn.fileno())

        # Echo Verification Test (PING - PONG)
        clt_sock.send(b"CLIENT_TEST_PING")

        # Server baca paket via ClientListener
        data = conn.recv(1024)
        log.prints("Server Received  =>", data.raw_bytes)

        if data.raw_bytes == b"CLIENT_TEST_PING":
            # Server balas ke Client
            conn.send(b"SERVER_TEST_PONG")

            # Client terima balasan
            reply = clt_sock.recv(1024)
            log.prints("Client Received  =>", reply.raw_bytes)
            log.printi("\nSERVER LIFECYCLE TEST PASSED PERFECTLY!")
    except Exception as e:
        log.printw("Test Exception =>", e)
    finally:
        if conn is not None:
            conn.close()
        if srv_sock is not None:
            srv_sock.close()
        if clt_sock is not None:
            clt_sock.close()
