# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy

import uuid
import smf
import base64

from typing import Dict, Any, Optional
from apps.utility.colors import CC
from ...transport import CRS


class SocketState:
    """
    Domain 1: Manajemen Konfigurasi & State Sesi.
    Menyimpan properti koneksi dan memvalidasi siklus hidup soket.
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
        self.protocol = protocol
        self.timeout = float(timeout)
        self.readsize = int(readsize)
        self.ratelimit = int(ratelimit)
        self.keepalive = keepalive
        self.mode = mode
        self.infotls = infotls

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
    Domain 2: Data Marshalling & Payload Transformation.
    Terisolasi untuk menangani translasi state dan parameter operasional menjadi skema JSON/Dict.
    """

    @staticmethod
    def build(
        state: SocketState,
        data: str | bytes = b"",
        infotls: bool = None,
        verify: bool = None,
        cert: str = None,
        key: str = None,
        ca: str = None,
        readsize: int = None,
        timeout: float = None,
        ratelimit: int = None,
        mode: str = None,
        protocol: str = None,
        close_session: bool = False,
    ) -> dict:
        # Mutasi state keamanan secara dinamis dari operasi spesifik
        if verify is not None:
            state.verify = verify

        if protocol is not None:
            if protocol.lower() in ["tls", "ssl"]:
                state.is_tls = True
                state.protocol = "tls"

        current_proto = "tls" if state.is_tls else state.protocol

        # Encoding muatan data
        data_str = ""
        if data:
            data_bytes = data.encode("utf-8") if isinstance(data, str) else data
            data_str = base64.b64encode(data_bytes).decode("utf-8")

        return {
            "primitive": "NETWORK_SEND",
            "host": state.host,
            "port": state.port,
            "data": data_str,
            "protocol": current_proto,
            "timeout": timeout if timeout is not None else state.timeout,
            "readsize": readsize if readsize is not None else state.readsize,
            "ratelimit": ratelimit if ratelimit is not None else state.ratelimit,
            "session_id": state.sessid,
            "keep-alive": state.keepalive,
            "close_session": close_session,
            "mode": mode if mode is not None else state.mode,
            "verify": verify if verify is not None else state.verify,
            "info_tls": infotls if infotls is not None else state.infotls,
            "tls-cert": cert,
            "tls-key": key,
            "tls-ca": ca,
            "goroutine": state.con,
        }


class TLSMetadata:
    """
    Data Transfer Object (DTO) untuk metadata TLS dari Go Engine.
    """

    def __init__(self, data: Dict[str, Any]):
        self.version: str = data.get("tls_version", "Unknown")
        self.cipher_suite: str = data.get("cipher_suite", "Unknown")
        self.protocol: str = data.get("protocol", "")
        self.hostname: str = data.get("hostname", "")
        self.handshake: bool = data.get("handshake", False)
        self.session_resume: bool = data.get("session_resume", False)

        # Sertifikat Data (Bisa None jika tidak ada)
        self.subject: Optional[str] = data.get("subject")
        self.issuer: Optional[str] = data.get("issuer")
        self.dns_name: list = data.get("dns_name", [])
        self.expires: Optional[str] = data.get("expires")
        self.cert_chain_count: int = data.get("cert_chain_count", 0)

    def __repr__(self):
        return f"<TLSMetadata {self.version} Cipher={self.cipher_suite} Host={self.hostname}>"


class SocketResponse:
    """
    Wrapper untuk mengelola respons dinamis dari CRS (IPC).
    Menyediakan Type-Safety, Property Access, dan Lazy Decoding.
    """

    def __init__(self, raw_response: Dict[str, Any]):
        self.raw_response = raw_response
        self._status: str = raw_response.get("status", "UNKNOWN")
        self._message: str = raw_response.get("message", "UNKNOWN")

        # Retrieve the "Data" payload from the response
        self._data: Dict[str, Any] = raw_response.get("data", {})

    @property
    def success(self) -> bool:
        """Mengembalikan True jika response berhasil"""
        return self._status.upper() == "SUCCESS"

    @property
    def status(self) -> str:
        """Mempermudah pengecekan status respons."""
        return self._status

    @property
    def message(self) -> str:
        """Mengembalikan pesan ERROR/SUCCESS/TIMEOUT."""
        return self._message

    @property
    def raw_bytes(self) -> bytes:
        """Mengembalikan raw bytes apa adanya."""
        raw_val = self._data.get("raw_bytes")

        if isinstance(raw_val, bytes):
            return raw_val

        if isinstance(raw_val, str) and raw_val:
            try:
                return base64.b64decode(raw_val)
            except Exception as e:
                smf.printd(f"Base64 decode error", e, level="ERROR")
                return raw_val.encode("utf-8")

        return b""

    @property
    def str_bytes(self) -> str:
        """Mengembalikan raw bytes sebagai UTF-8."""
        return self.raw_bytes.decode("utf-8", errors="ignore")

    @property
    def hex_bytes(self) -> str:
        """Mengembalikan bytes berupa HEX"""
        return self._data.get("hex_bytes", "")

    @property
    def read_bytes(self) -> int:
        """Mengembalikan bytes berupa angka"""
        return self._data.get("read_bytes", 0)

    @property
    def ip(self) -> str:
        """Mengecek IP Server"""
        return self._data.get("ip", "unknown")

    @property
    def local_ip(self) -> str:
        """Mengecek IP keluar sebelum ke internet global"""
        return self._data.get("local_ip", "unknown")

    @property
    def rtt_ms(self) -> int:
        """Round Trip Time dalam millisecond."""
        return self._data.get("rtt_ms", 0)

    @property
    def isreused(self) -> bool:
        """Melihat apakah koneksi yang di gunakan sama dengan sebelumnya"""
        return self._data.get("is_reused", False)

    @property
    def checked_type(self) -> str:
        """Tipe refleksi interface Go (reflect.TypeOf(conn).String())"""
        return self._data.get("Cheked", "")

    @property
    def status_tls(self) -> bool:
        """Menerjemahkan string boolean dari Go (strconv.FormatBool) ke native Python bool."""
        val = self._data.get("isAlreadyTLS", "false")
        return val.lower() == "true"

    @property
    def tls(self) -> Optional[TLSMetadata]:
        """Objek TLSMetadata jika info_tls tersedia, sebaliknya None."""
        tls_data = self._data.get("info_tls")
        if tls_data and isinstance(tls_data, dict):
            return TLSMetadata(tls_data)
        return None

    def __bool__(self):
        """Memungkinkan sintaks: if response: ..."""
        return self.status

    def __repr__(self):
        return f"<SocketResponse Status={self.status} Read={self.read_bytes}b RTT={self.rtt_ms}ms>"


class Socket(SocketState):
    """
    Domain 3: Facade Antarmuka Eksternal.
    Mewarisi SocketState untuk mempertahankan kompatibilitas atribut (Backward Compatibility).
    Hanya berfokus pada eksekusi instruksi jaringan ke Engine Go.
    """

    def __init__(self, *args, **kwargs):
        # 1. Setup semua variabel dan state dari SocketState
        super().__init__(*args, **kwargs)

        # 2. Langsung tembak instruksi 'open' ke Go Engine
        self.initial_response = self.open()

    def open(self, timeout: float = None) -> SocketResponse:
        self._ensure_open("open")
        packet = IPCPayloadBuilder.build(
            state=self,
            mode="open",
            timeout=timeout,
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)

        return SocketResponse(resp)

    def send(
        self,
        data: str | bytes,
        timeout: float = None,
        mode: str = "send",
        **kwargs,
    ) -> SocketResponse:
        self._ensure_open("send")
        packet = IPCPayloadBuilder.build(
            state=self,
            data=data,
            timeout=timeout,
            mode=mode,
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)

        return SocketResponse(resp)

    def recv(self, readsize: int = None, timeout: float = 0.3) -> SocketResponse:
        self._ensure_open("receive")
        packet = IPCPayloadBuilder.build(
            state=self,
            readsize=readsize,
            timeout=timeout,
            infotls=False,
            mode="recv",
            close_session=False,
        )

        resp = CRS.send(packet)

        return SocketResponse(resp)

    def uptls(
        self, cert: str, key: str, ca: str = None, verify: bool = True
    ) -> SocketResponse:
        if self.is_tls:
            smf.printd("The connection is already using TLS", level="WARN")
            return {"status": "WARN", "message": "Already TLS"}

        packet = IPCPayloadBuilder.build(
            state=self,
            verify=verify,
            mode="upgrade_tls",
            protocol="tls",
            cert=cert,
            key=key,
            ca=ca,
            infotls=True,
            close_session=False,
        )

        resp = CRS.send(packet)

        if resp.get("status") == "SUCCESS":
            self.is_tls = True

        return SocketResponse(resp)

    def close(self) -> SocketResponse:
        if self._is_closed:
            return {"status": "already_closed", "session_id": self.sessid}

        packet = IPCPayloadBuilder.build(state=self, mode="close", close_session=True)

        resp = CRS.send(packet)
        self._is_closed = True

        return SocketResponse(resp)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self):
        tls_state = "TLS" if self.is_tls else "TCP"
        return f"<Socket host='{self.host}:{self.port}' proto='{tls_state}' sessid='{self.sessid}' closed={self._is_closed}>"
