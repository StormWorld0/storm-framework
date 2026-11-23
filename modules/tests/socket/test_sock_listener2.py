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
    clt1_sock = None
    clt2_sock = None
    conn1 = None
    conn2 = None
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

        # Variable penampung
        client = {
            "c1": [],
            "c2": [],
        }

        # Worker Thread untuk menjalankan accept()
        def accept_worker(name):
            conn, resp = srv_sock.accept()
            client[name].append((conn, resp))

        t1 = threading.Thread(target=accept_worker, args=("c1",), daemon=True)
        t2 = threading.Thread(target=accept_worker, args=("c2",), daemon=True)
        t1.start()
        t2.start()

        # Beri jeda 100ms 
        time.sleep(0.1)

        # Client Simulator
        clt1_sock = net.Socket()
        clt2_sock = net.Socket()
        
        clt1_sock.socket(clt1_sock.AF_INET, clt1_sock.SOCK_STREAM)
        clt2_sock.socket(clt2_sock.AF_INET, clt2_sock.SOCK_STREAM)
        
        log.prints("Socket ClientFD (1) =>", clt1_sock.fileno())
        log.prints("Socket ClientFD (2) =>", clt2_sock.fileno())

        resp1 = clt1_sock.connect((host, port))
        resp2 = clt2_sock.connect((host, port))
        if resp1.ok and resp2.ok:
            log.prints("Client Connected =>", f"{host}:{port}")
        else:
            log.printw("Client (1) Connect Failed =>", resp1.message)
            log.printw("Client (2) Connect Failed =>", resp2.message)
            return

        # Tunggu thread accept() menerima koneksi
        t1.join(timeout=2.0)
        t2.join(timeout=2.0)

        conn1, resp1 = client["c1"][0]
        conn2, resp2 = client["c2"][0]
        
        if not resp1.ok:
            log.printw("(1) Accept Error     =>", resp1.message)
            return
        if not resp2.ok:
            log.printw("(2) Accept Error     =>", resp2.message)
            return

        log.prints("Accepted ClientFD (1) =>", conn1.fileno())
        log.prints("Accepted ClientFD (2) =>", conn2.fileno())

        # Echo Verification Test (PING - PONG)
        clt1_sock.send(b"CLIENT1_TEST_PING")
        clt2_sock.send(b"CLIENT2_TEST_PING")

        # Server baca paket via ClientListener
        data1 = conn1.recv(1024)
        log.prints("Server Received  =>", data1.raw_bytes)
        if data1.raw_bytes == b"CLIENT1_TEST_PING":
            conn1.send(b"SERVER_TEST_PONG")

            reply1 = clt1_sock.recv(1024)
            log.prints("Client (1) Received  =>", reply1.raw_bytes)

        
        data2 = conn2.recv(1024)
        log.prints("Server Received  =>", data2.raw_bytes)
        if data2.raw_bytes == b"CLIENT2_TEST_PING":
            conn2.send(b"SERVER_TEST_PONG")
            
            reply2 = clt2_sock.recv(1024)
            log.prints("Client (2) Received  =>", reply2.raw_bytes)
            
        log.prints()
        log.printi("SERVER LIFECYCLE TEST PASSED PERFECTLY!")
    except Exception as e:
        log.printw("Test Exception =>", e)
    finally:
        if conn1 is not None:
            conn1.close(conn1.fileno())
        if conn2 is not None:
            conn2.close(conn2.fileno())
        if clt1_sock is not None:
            clt1_sock.close(clt1_sock.fileno())
        if clt2_sock is not None:
            clt2_sock.close(clt2_sock.fileno())
        if srv_sock is not None:
            srv_sock.close(srv_sock.fileno())
            
