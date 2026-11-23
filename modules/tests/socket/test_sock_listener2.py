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


BACKLOG = 5
PING_PONG_TIMEOUT = 2.0
RECV_BUFFER_SIZE = 1024
PONG_PAYLOAD = b"SERVER_TEST_PONG"


def _setup_listener(net, log):
    sock = net.Socket()
    srv_sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    log.printi("Server RawFD  =>", sock.fileno())

    sock.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
    resp = sock.bind(("127.0.0.1", 0))
    if not resp.ok:
        log.printw("Bind Failed     =>", resp.message)
        return sock, None, None, False

    host, port = sock.getsockname()
    log.printi("Bound to Address =>", f"{host}:{port}")

    resp = sock.listen(BACKLOG)
    if not resp.ok:
        log.printw("Listen Failed   =>", resp.message)
        return sock, host, port, False

    log.prints(f"Status Listen    => Success (Backlog: {BACKLOG})")
    return sock, host, port, True


def _accept_concurrent(sock, count=2, timeout=PING_PONG_TIMEOUT):
    results = [None] * count
    threads = []

    def worker(idx):
        results[idx] = sock.accept()

    for idx in range(count):
        t = threading.Thread(target=worker, args=(idx,), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=timeout)

    accepted = []
    for idx, item in enumerate(results):
        if item is None:
            return None, f"Accept worker ({idx + 1}) timed out"
        conn, resp = item
        if not resp.ok:
            return None, f"Accept ({idx + 1}) failed: {resp.message}"
        accepted.append(conn)

    return accepted, None


def _connect_clients(net, host, port, count, log):
    clients = []
    for idx in range(count):
        sock = net.Socket()
        sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        log.prints(f"Socket ClientFD ({idx + 1}) =>", sock.fileno())

        resp = sock.connect((host, port))
        if not resp.ok:
            log.printw(f"Client ({idx + 1}) Connect Failed =>", resp.message)
            _cleanup_sockets(log, [*clients, sock])
            return None

        clients.append(sock)

    log.prints("Client Connected =>", f"{host}:{port}")
    return clients


def _run_ping_pong(clt_sock, conn, ping_msg, pong_msg, idx, log):
    clt_sock.send(ping_msg)
    data = conn.recv(RECV_BUFFER_SIZE)
    raw_in = getattr(data, "raw_bytes", None)
    log.prints(f"Server Received ({idx}) =>", raw_in)

    if raw_in != ping_msg:
        log.printw(f"Unexpected payload ({idx}) =>", raw_in)
        return False

    conn.send(pong_msg)
    reply = clt_sock.recv(RECV_BUFFER_SIZE)
    raw_out = getattr(reply, "raw_bytes", None)
    log.prints(f"Client ({idx}) Received  =>", raw_out)

    if raw_out != pong_msg:
        log.printw(f"Unexpected reply ({idx}) =>", raw_out)
        return False

    return True


def _cleanup_sockets(log, sockets):
    for sock in sockets:
        if sock is None:
            continue
        try:
            fd = sock.fileno()
            if fd is not None and fd >= 0:
                sock.close(fd)
        except Exception as e:
            log.printw("Cleanup Close Warning =>", e)


def execute(options, net, log):
    worker_count = 2
    sock = None
    client_socks = []
    accepted_conns = []

    try:
        sock, host, port, ok = _setup_listener(net, log)
        if not ok:
            return

        accept_box = []
        def run_accepts():
            accept_box.append(_accept_concurrent(sock, count=worker_count, timeout=PING_PONG_TIMEOUT))

        acceptor_thread = threading.Thread(target=run_accepts, daemon=True)
        acceptor_thread.start()
        time.sleep(0.1)

        connected = _connect_clients(net, host, port, worker_count, log)
        if connected is None:
            return
        client_socks = connected

        acceptor_thread.join(timeout=PING_PONG_TIMEOUT + 0.5)
        if not accept_box:
            log.printw("Accept Error => Acceptor thread did not complete")
            return

        conns, accept_err = accept_box[0]
        if accept_err is not None:
            log.printw("Accept Error =>", accept_err)
            return
        accepted_conns = conns

        for idx, conn in enumerate(accepted_conns, start=1):
            log.prints(f"Accepted ClientFD ({idx}) =>", conn.fileno())

        for idx, (clt_sock, conn) in enumerate(zip(client_socks, accepted_conns), start=1):
            ping_msg = f"CLIENT{idx}_TEST_PING".encode()
            if not _run_ping_pong(clt_sock, conn, ping_msg, PONG_PAYLOAD, idx, log):
                log.printw(f"Ping-Pong Failed on Client ({idx})")
                return

        log.prints()
        log.printi("SERVER LIFECYCLE TEST PASSED PERFECTLY!")
    except Exception as e:
        log.printw("Test Exception =>", e)
    finally:
        _cleanup_sockets(log, accepted_conns)
        _cleanup_sockets(log, client_socks)
        _cleanup_sockets(log, [sock])
        
