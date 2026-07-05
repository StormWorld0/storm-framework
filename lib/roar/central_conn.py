import grpc
import time
import smf

from lib.core.engine import GoEngineManager
from ..core import c2_console

from internal.proto.rpc import services_pb
from internal.proto.rpc import services_pb_grpc
from internal.proto.common import common_pb


# ==========================================
# GRP/mTLS CONNECTION INITIATOR
# ==========================================
def _get_grpc_client():
    STORM_CA_CERT = "data/smf_ca.crt"
    OPERATOR_KEY = "data/smf_ca.key"

    try:
        with open(STORM_CA_CERT, "rb") as f:
            root_ca = f.read()
        with open(OPERATOR_KEY, "rb") as f:
            client_key = f.read()

        credentials = grpc.ssl_channel_credentials(
            root_certificates=root_ca, private_key=client_key, certificate_chain=root_ca
        )

        channel = grpc.secure_channel("127.0.0.1:31337", credentials)
        return services_pb_grpc.SliverRPCStub(channel)
    except FileNotFoundError as e:
        smf.printd("Missing cryptography assets", e, level="ERROR")
        return None


# ==========================================
# CORE PIPELINE: MODULES -> HANDLER -> TARGET
# ==========================================
def process_attack_flow(module_data):
    """
    Entry point tunggal yang dipanggil oleh modul.
    """
    # 1. JIT Booting: Nyalakan Go Engine hanya saat dibutuhkan
    engine = GoEngineManager()
    if not engine.start():
        smf.printd("Aborting attack flow: Backend engine offline.", level="WARN")
        return

    # 2. Bangun Kredensial gRPC
    rpc_client = _get_grpc_client()
    if not rpc_client:
        return

    # 3. Ekstraksi & Deploy Listener
    lhost = module_data.get("LHOST", "0.0.0.0")
    lport = int(module_data.get("LPORT", "8080"))

    try:
        smf.printd(f"Deploying MTLS listener on backend -> {lhost}:{lport}", level="INFO")
        req = services_pb.StartMTLSListenerReq(Host=lhost, Port=lport)
        rpc_client.StartMTLSListener(req)
    except grpc.RpcError as e:
        smf.printd("Backend listener failed", e.details(), level="ERROR")
        return

    # 4. Polling Koneksi Masuk
    smf.printf("[*] Listener active. Scanning connection queue (Ctrl+C to abort)...")
    empty_req = common_pb.Empty()
    session_id = None

    while True:
        try:
            res = rpc_client.GetSessions(empty_req)
            if len(res.Sessions) > 0:
                session_id = res.Sessions[-1].ID
                break
            time.sleep(1)
        except KeyboardInterrupt:
            smf.printf("\n[*] Scan aborted by operator.")
            _teardown_backend(rpc_client, lport, None)
            return

    # 5. Lempar Eksekusi ke Modul REPL Mandiri (Terminal Terkunci di Sini)
    if session_id:
        c2_console.start_interactive_session(session_id, rpc_client)

    # 6. Fase Cleanup (Terpicu otomatis saat REPL di exit)
    smf.printf(f"[*] Destroying active state for session {session_id}...")
    _teardown_backend(rpc_client, lport, session_id)
    smf.printf("[+] Handler sequence completed. Storm Core REPL unlocked.")


# ==========================================
# BACKEND CLEANUP
# ==========================================
def _teardown_backend(rpc_client, lport, session_id):
    """
    Membersihkan listener dan membunuh sesi di sliver-server.
    Dilepas tanpa pengaman agar smf bisa menangkap traceback jika terjadi anomali gRPC.
    """
    try:
        if session_id:
            smf.printd(f"[*] Sending kill signal to session {session_id}", level="INFO")
            # Langsung hajar dengan eksekusi real
            req_kill = services_pb.SessionReq(SessionID=session_id)
            rpc_client.KillSession(req_kill)

        smf.printd(f"[*] Stopping backend listener on port {lport}", level="INFO")
        # Matikan port listener secara agresif
        req_stop = services_pb.StopListenerReq(Port=lport)
        rpc_client.StopMTLSListener(req_stop)

    except grpc.RpcError as e:
        smf.printd("Cleanup warning: gRPC Error", e.details(), level="ERROR")
    except AttributeError as e:
        smf.printd("Protobuf attribute mismatch during teardown", e, level="ERROR")
