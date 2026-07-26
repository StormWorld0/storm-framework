# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import uuid
import smf
import base64

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
        timeout: float = 10.0,
        readsize: int = 0,
        ratelimit: int = 0,
        sessid: str = "",
        keep_alive: bool = True,
        mode: str = "send_only",
        verify: bool = True,
        cert: str = "",
        key: str = "",
        ca: str = "",
        **kwargs,
    ):
        # State Initialization
        self.host = host
        self.port = int(port)
        self.protocol = protocol
        self.timeout = float(timeout)
        self.readsize = int(readsize)
        self.ratelimit = int(ratelimit)
        self.keep_alive = keep_alive
        self.mode = mode
        self.verify = verify
        self.cert = cert
        self.key = key
        self.ca = ca

        # Auto-generate Session ID jika belum ada (agar stream terisolasi di Go IPC)
        self.sessid = sessid if sessid else f"smf_sess_{uuid.uuid4().hex[:12]}"
        self.is_tls = False
        self._is_closed = False

        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )

    def _build_packet(
        self,
        data: str = "",
        verify: bool = None,
        cert: str = None,
        key: str = None,
        ca: str = None,
        readsize: int = None,
        timeout: float = None,
        ratelimit: int = None,
        mode: str = None,
        close_session: bool = False,
    ) -> dict:
        """Internal Helper: Menyiapkan schema JSON/Dict untuk dikirim via IPC ke Go"""

        # Ubah data ke b64 & string
        data_str = ""
        if data:
            data_bytes = data.encode("utf-8") if isinstance(data, str) else data
            data_str = base64.b64encode(data_bytes).decode("utf-8")

        return {
            "primitive": "NETWORK_SEND",
            "host": self.host,
            "port": self.port,
            "data": data_str,
            "protocol": protocol if protocol is not None else self.protocol,
            "timeout": timeout if timeout is not None else self.timeout,
            "readsize": readsize if readsize is not None else self.readsize,
            "ratelimit": ratelimit if ratelimit is not None else self.ratelimit,
            "session_id": self.sessid,
            "keep-alive": self.keep_alive,
            "close_session": close_session,
            "mode": mode if mode is not None else self.mode,
            "verify": verify if verify is not None else self.verify,
            "tls-cert": cert if cert is not None else self.cert,
            "tls-key": key if key is not None else self.key,
            "tls-ca": ca if ca is not None else self.ca,
        }

    def send(
        self,
        data: str,
        verify: bool = None,
        cert: str = None,
        key: str = None,
        ca: str = None,
        timeout: float = None,
        ratelimit: int = None,
        mode: str = "send_only",
        **kwargs,
    ) -> dict:
        """Kirim payload ke target via Go Engine"""
        if self._is_closed:
            smf.printd("Cannot send on a closed Socket session.", level="ERROR")
            raise RuntimeError("Cannot execute send() on a closed Socket session.")

        packet = self._build_packet(
            data=data,
            verify=verify,
            cert=cert,
            key=key,
            ca=ca,
            timeout=timeout,
            ratelimit=ratelimit,
            mode=mode,
            close_session=False,
        )
        return CRS.send(packet)

    def recv(self, readsize: int = None) -> dict:
        """
        Receive/Read data dari active IPC Session.
        Menggunakan mode 'recv_only' untuk instruksi khusus ke CRS engine.
        """
        if self._is_closed:
            smf.printd("Cannot receive on a closed Socket session", level="ERROR")
            raise RuntimeError("Cannot execute recv() on a closed Socket session.")

        packet = self._build_packet(
            data="",
            readsize=readsize,
            mode="recv_only",
            close_session=False,
        )

        return CRS.send(packet)

    # Upgrade koneksi ke TLS
    def uptls(self, cert: str, key: str, ca: str = None, verify: bool = None) -> dict:
        """
        Mengirim instruksi TLS UPGRADE ke CRS Engine (Go Backend)
        untuk membungkus TCP connection yang sedang aktif menjadi TLS.
        """
        if self.is_tls:
            smf.printd("The connection is already using TLS", level="WARN")
            return {"status": "WARN", "message": "Already TLS"}
        packet = self._build_packet(
            data="",
            cert=cert,
            key=key,
            ca=ca,
            verify=verify,
            mode="duplex",
            protocol="tls",
            close_session=False,
        )

        # Kirim command upgrade ke Go Engine via IPC
        response = CRS.send(packet)

        if response.get("status") == "SUCCESS":
            self.is_tls = True
            return response.get("data", {})  # Kembalikan info TLS (version, cipher, dll)
        else:
            raise Exception(f"TLS Upgrade Failed: {response.get('message')}")

        return response

    # Close season aktif dan lepas koneksi
    def close(self) -> dict:
        """Mengirim signal terminasi ke CRS Engine untuk menghapus Session ID."""
        if self._is_closed:
            return {"status": "already_closed", "session_id": self.sessid}

        packet = self._build_packet(data="", mode="send_only", close_session=True)
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
        tls_state = "TLS" if self.is_tls else "TCP"
        return f"<Socket host='{self.host}:{self.port}' proto='{tls_state}' sessid='{self.sessid}' closed={self._is_closed}>"
