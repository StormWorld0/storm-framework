import smf
import uuid
import base64

from apps.utility.colors import CC


class SocketState:
    """
    Manajemen Konfigurasi & State Sesi.
    Menyimpan properti koneksi dan memvalidasi siklus hidup soket.
    """

    def __init__(
        self,
        host: str = "",
        port: int = 0,
        addr_fam: str | int = 0,
        stype: str | int = 0,
        sproto: str | int = 0,
        level: str | int = 0,
        name: str | int = 0,
        value: int = 0,
        timeout: float = 10.0,
        readsize: int = 0,
        ratelimit: int = 0,
        sessid: str = "",
        keepalive: bool = True,
        mode: str = "open",
        verify: bool = True,
        infotls: bool = False,
        cert: str = "",
        key: str = "",
        ca: str = "",
        con: int = 0,
        **kwargs,
    ):
        self.host = host
        self.port = int(port)
        self._timeout = float(timeout)
        self.readsize = int(readsize)
        self.ratelimit = int(ratelimit)
        self.keepalive = keepalive
        self.mode = mode
        self.infotls = infotls

        # AF_* and SOCK_* and IPPROTO_*
        self.af = addr_fam
        self.stype = stype
        self.sproto = sproto

        #
        self.level = level
        self.name = name
        self.value = int(value)

        # Isolasi sesi Go IPC
        self.sessid = sessid if sessid else f"smf_sess_{uuid.uuid4().hex[:12]}"
        self._is_closed = False

        # Status Keamanan TLS
        self.is_tls = False
        self.verify = verify
        self.cert = cert
        self.key = key
        self.ca = ca

        # Goroutine not support
        self.con = con

        if kwargs:
            smf.printf(
                f"[!] {CC.YELLOW}Unrecognized parameters dropped =>{CC.RESET}", kwargs
            )

    def _ensure_open(self, operation: str):
        """Validasi internal untuk mencegah eksekusi operasi pada sesi yang tertutup."""
        if self._is_closed:
            smf.printd(f"Cannot {operation} on a closed Socket session.", level="ERROR")
            raise RuntimeError(
                f"Cannot execute {operation}() on a closed Socket session."
            )


class IPCPayloadBuilder:
    """
    Data Marshalling & Payload Transformation.
    Terisolasi untuk menangani translasi state dan parameter operasional menjadi skema JSON/Dict.
    """

    @staticmethod
    def build(
        state: SocketState,
        host: str = None,
        port: str = None,
        data: str | bytes = b"",
        addr_fam: str | int = None,
        stype: str | int = None,
        sproto: str | int = None,
        level: str | int = None,
        name: str | int = None,
        value: int = None,
        infotls: bool = None,
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
        # Mutasi state keamanan secara dinamis dari operasi spesifik
        if verify is not None:
            state.verify = verify

        if addr_fam is not None:
            state.addr_fam = addr_fam

        # Encoding muatan data
        data_str = ""
        if data:
            data_bytes = data.encode("utf-8") if isinstance(data, str) else data
            data_str = base64.b64encode(data_bytes).decode("utf-8")

        return {
            "primitive": "SOCKET_SEND",
            "host": host if host is not None else state.host,
            "port": int(port) if port is not None else state.port,
            "data": data_str,
            "addr-fam": addr_fam if addr_fam is not None else state.af,
            "stype": stype,
            "sproto": sproto,
            "opt-level": level,
            "opt-name": name,
            "opt-value": int(value),
            "timeout": float(timeout) if timeout is not None else state._timeout,
            "readsize": readsize if readsize is not None else state.readsize,
            "ratelimit": ratelimit if ratelimit is not None else state.ratelimit,
            "session_id": state.sessid,
            "keep-alive": state.keepalive,
            "close-session": close_session,
            "mode": mode if mode is not None else state.mode,
            "verify": verify if verify is not None else state.verify,
            "info_tls": infotls if infotls is not None else state.infotls,
            "tls-cert": cert,
            "tls-key": key,
            "tls-ca": ca,
            "goroutine": state.con,
        }
