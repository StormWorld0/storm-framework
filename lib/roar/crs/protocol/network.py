# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import uuid
import smf
from apps.utility.colors import CC
from ..transport import CRS


class Socket:
    """
    Stateful Socket Wrapper over Golang IPC Engine (CRS).
    Manages session lifecycle, persistent streams, and socket operations.
    """

    def __init__(
        self,
        host: str = "",
        port: int = 0,
        protocol: str = "tcp",
        timeout: float = 5.0,
        encoding: str = "",
        readsize: int = 4096,
        ratelimit: int = 0,
        sessid: str = "",
        keep_alive: bool = True,  # Default True untuk persistent socket
        verify: bool = True,
        cert: str = "",
        key: str = "",
        ca: str = "",
        **kwargs,
    ):
        # State Initialization
        self.host = host
        self.port = port
        self.protocol = protocol
        self.timeout = timeout
        self.encoding = encoding
        self.readsize = readsize
        self.ratelimit = ratelimit
        self.keep_alive = keep_alive
        self.verify = verify
        self.cert = cert
        self.key = key
        self.ca = ca

        # Auto-generate Session ID jika belum ada (agar stream terisolasi di Go IPC)
        self.sessid = sessid if sessid else f"smf_sess_{uuid.uuid4().hex[:12]}"
        self._is_closed = False

        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )

    def _build_packet(
        self, body: str = "", mode: str = "duplex", close_session: bool = False
    ) -> dict:
        """Internal Helper: Menyiapkan schema JSON/Dict untuk dikirim via IPC ke Go"""
        return {
            "primitive": "NETWORK_SEND",
            "host": self.host,
            "port": self.port,
            "body": body,
            "protocol": self.protocol,
            "timeout": self.timeout,
            "encoding": self.encoding,
            "readsize": self.readsize,
            "ratelimit": self.ratelimit,
            "session_id": self.sessid,
            "keep-alive": self.keep_alive,
            "close_session": close_session,
            "mode": mode,
            "verify": self.verify,
            "tls-cert": self.cert,
            "tls-key": self.key,
            "tls-ca": self.ca,
        }

    def send(self, body: str, mode: str = "duplex") -> dict:
        """Kirim payload ke target via Go Engine"""
        if self._is_closed:
            raise RuntimeError("Cannot send on a closed Socket session.")

        packet = self._build_packet(body=body, mode=mode, close_session=False)
        return CRS.send(packet)

    def recv(self, readsize: int = None) -> dict:
        """
        Receive/Read data dari active IPC Session.
        Menggunakan mode 'recv_only' untuk instruksi khusus ke Go engine.
        """
        if self._is_closed:
            raise RuntimeError("Cannot receive on a closed Socket session.")

        # Izinkan override readsize jika dibutuhkan per-read call
        original_readsize = self.readsize
        if readsize is not None:
            self.readsize = readsize

        packet = self._build_packet(body="", mode="recv_only", close_session=False)
        response = CRS.send(packet)

        # Restore default readsize
        self.readsize = original_readsize
        return response

    def close(self) -> dict:
        """Mengirim signal terminasi ke Go Engine untuk menghapus Session ID"""
        if self._is_closed:
            return {"status": "already_closed", "session_id": self.sessid}

        packet = self._build_packet(body="", mode="send_only", close_session=True)
        res = CRS.send(packet)
        self._is_closed = True
        return res

    # --- BONUS OOP FEATURE: Context Manager & Resource Lifecycle ---

    def __enter__(self):
        """Mendukung syntax 'with Socket(...) as sock:'"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Otomatis memanggil .close() ketika keluar dari block 'with'"""
        self.close()

    def __repr__(self):
        return f"<Socket host='{self.host}:{self.port}' proto='{self.protocol}' sessid='{self.sessid}' closed={self.is_closed}>"
