# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy (Refactored)
import time
from typing import Optional, Union, List, Tuple

# Pastikan import Socket Anda benar sesuai struktur framework
from ..network import Socket


class TelnetCmd:
    """Konstanta untuk Telnet Commands (RFC 854 & Extensions)"""

    EOF = b"\xec"
    SUSP = b"\xed"
    ABORT = b"\xee"
    EOR = b"\xef"
    SE = b"\xf0"
    NOP = b"\xf1"
    DM = b"\xf2"
    BRK = b"\xf3"
    IP = b"\xf4"
    AO = b"\xf5"
    AYT = b"\xf6"
    EC = b"\xf7"
    EL = b"\xf8"
    GA = b"\xf9"
    SB = b"\xfa"
    WILL = b"\xfb"
    WONT = b"\xfc"
    DO = b"\xfd"
    DONT = b"\xfe"
    IAC = b"\xff"


class TelnetOpt:
    """Konstanta untuk Telnet Options (RFC Extensions)"""

    BINARY = b"\x00"
    ECHO = b"\x01"
    RCP = b"\x02"
    SGA = b"\x03"
    NAMS = b"\x04"
    STATUS = b"\x05"
    TM = b"\x06"
    RCTE = b"\x07"
    NAOL = b"\x08"
    NAOP = b"\x09"
    EOR = b"\x19"
    TTYPE = b"\x18"
    NAWS = b"\x1f"
    TSPEED = b"\x20"
    LFLOW = b"\x21"
    LINEMODE = b"\x22"
    XDISPLOC = b"\x23"
    OLD_ENVIRON = b"\x24"
    NEW_ENVIRON = b"\x27"


class TelnetClient:
    """
    Telnet Protocol Wrapper di atas Socket Engine.
    Terintegrasi dengan TelnetCmd & TelnetOpt untuk kontrol granular dan Type-Safety.
    """

    def __init__(self, host: str, port: int = 23, timeout: float = 10.0, **kwargs):
        """Open koneksi Telnet di atas TCP Socket"""
        self.sock = Socket(host=host, port=port, timeout=timeout, **kwargs)
        self.timeout = timeout
        self._buffer = b""
        self._iac_fragment = b""

    def _negotiate_iac(self, raw_data: bytes) -> bytes:
        data = self._iac_fragment + raw_data
        self._iac_fragment = b""

        clean_data = bytearray()
        i = 0
        length = len(data)

        while i < length:
            if data[i : i + 1] == TelnetCmd.IAC:
                if i + 1 < length and data[i + 1 : i + 2] == TelnetCmd.IAC:
                    clean_data.append(255)
                    i += 2
                    continue

                if i + 1 >= length:
                    self._iac_fragment = data[i:]
                    break

                cmd = data[i + 1 : i + 2]

                if cmd in (TelnetCmd.DO, TelnetCmd.DONT, TelnetCmd.WILL, TelnetCmd.WONT):
                    if i + 2 >= length:
                        self._iac_fragment = data[i:]
                        break

                    opt = data[i + 2 : i + 3]

                    # Auto-Rejection / Hardened Fallback
                    if cmd in (TelnetCmd.DO, TelnetCmd.DONT):
                        self.sock.send(TelnetCmd.IAC + TelnetCmd.WONT + opt)
                    elif cmd in (TelnetCmd.WILL, TelnetCmd.WONT):
                        self.sock.send(TelnetCmd.IAC + TelnetCmd.DONT + opt)

                    i += 3
                elif cmd == TelnetCmd.SB:
                    end_sb = data.find(TelnetCmd.IAC + TelnetCmd.SE, i)
                    if end_sb == -1:
                        self._iac_fragment = data[i:]
                        break
                    else:
                        i = end_sb + 2
                elif cmd in (
                    TelnetCmd.NOP,
                    TelnetCmd.DM,
                    TelnetCmd.BRK,
                    TelnetCmd.IP,
                    TelnetCmd.AO,
                    TelnetCmd.AYT,
                    TelnetCmd.EC,
                    TelnetCmd.EL,
                    TelnetCmd.GA,
                    TelnetCmd.EOF,
                    TelnetCmd.SUSP,
                    TelnetCmd.ABORT,
                    TelnetCmd.EOR,
                ):
                    i += 2
                else:
                    i += 2
            else:
                clean_data.append(data[i])
                i += 1

        return bytes(clean_data)

    def read(
        self,
        expected: Union[str, bytes, List[Union[str, bytes]]] = b"",
        timeout: Optional[float] = None,
        raw: bool = False,
    ) -> Tuple[Union[str, bytes], int]:
        """Membaca Response Telnet (Tuple return: data, match_index)"""

        # Guard: Jika expected kosong, buat fallback list kosong agar tidak loop tanpa henti
        if expected == "" or expected == b"":
            expected_list = []
        elif not isinstance(expected, (list, tuple)):
            expected_list = [expected]
        else:
            expected_list = expected

        expected_bytes = [
            item.encode("utf-8") if isinstance(item, str) else item
            for item in expected_list
        ]

        # Fix bug `timeout or self.timeout` untuk mengakomodasi timeout=0
        wait_time = timeout if timeout is not None else self.timeout
        start_time = time.time()

        while True:
            # Jika punya expected condition, periksa buffer
            if expected_bytes:
                for idx, exp in enumerate(expected_bytes):
                    if exp in self._buffer:
                        pos = self._buffer.find(exp) + len(exp)
                        result = self._buffer[:pos]
                        self._buffer = self._buffer[pos:]

                        return (
                            result if raw else result.decode("utf-8", errors="ignore")
                        ), idx

            # Cek waktu tunggu (Timeout)
            if (time.time() - start_time) >= wait_time:
                break

            resp = self.sock.recv(readsize=4096)

            if resp.success == "SUCCESS" and not resp.raw_bytes:
                break

            if resp.raw_bytes:
                clean_chunk = self._negotiate_iac(resp.raw_bytes)
                self._buffer += clean_chunk
            else:
                # Cegah CPU Spiking jika soket non-blocking tapi belum ada data
                time.sleep(0.01)

        # Timeout / Selesai membaca: Kembalikan sisa buffer (jika ada)
        res = self._buffer
        self._buffer = b""
        response = res if raw else res.decode("utf-8", errors="ignore")
        return response, -1

    def send(
        self,
        command: Union[str, bytes],
        expected: Union[str, bytes, List[Union[str, bytes]]] = b"",
        timeout: Optional[float] = None,
        raw: bool = False,
    ) -> Tuple[Union[str, bytes], int]:
        """Mengirim data Telnet dan langsung membaca Response"""
        if isinstance(command, str):
            cmd_payload = f"{command}\r\n".encode("utf-8")
        else:
            cmd_payload = command + b"\r\n"

        self.sock.send(cmd_payload, timeout=timeout)
        return self.read(expected, timeout, raw)

    def close(self):
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
