# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy
import time

from typing import Optional, Union
from ..network import Socket


class TelnetCmd:
    """Konstanta untuk Telnet Commands (RFC 854 & Extensions)"""

    EOF = b"\xec"  # 236 (End of File)
    SUSP = b"\xed"  # 237 (Suspend Process)
    ABORT = b"\xee"  # 238 (Abort Process)
    EOR = b"\xef"  # 239 (End of Record - RFC 885)
    SE = b"\xf0"  # 240 (Subnegotiation End)
    NOP = b"\xf1"  # 241 (No Operation)
    DM = b"\xf2"  # 242 (Data Mark - Sync)
    BRK = b"\xf3"  # 243 (Break)
    IP = b"\xf4"  # 244 (Interrupt Process)
    AO = b"\xf5"  # 245 (Abort Output)
    AYT = b"\xf6"  # 246 (Are You There)
    EC = b"\xf7"  # 247 (Erase Character)
    EL = b"\xf8"  # 248 (Erase Line)
    GA = b"\xf9"  # 249 (Go Ahead)
    SB = b"\xfa"  # 250 (Subnegotiation Begin)
    WILL = b"\xfb"  # 251 (Negotiation: WILL)
    WONT = b"\xfc"  # 252 (Negotiation: WONT)
    DO = b"\xfd"  # 253 (Negotiation: DO)
    DONT = b"\xfe"  # 254 (Negotiation: DONT)
    IAC = b"\xff"  # 255 (Interpret As Command)


class TelnetOpt:
    """Konstanta untuk Telnet Options (RFC Extensions)"""

    BINARY = b"\x00"  # 0  (8-bit Binary Transmission)
    ECHO = b"\x01"  # 1  (Echo Data)
    RCP = b"\x02"  # 2  (Reconnection)
    SGA = b"\x03"  # 3  (Suppress Go Ahead)
    NAMS = b"\x04"  # 4  (Approx Message Size)
    STATUS = b"\x05"  # 5  (Status Option)
    TM = b"\x06"  # 6  (Timing Mark)
    RCTE = b"\x07"  # 7  (Remote Controlled Trans and Echo)
    NAOL = b"\x08"  # 8  (Output Line Width)
    NAOP = b"\x09"  # 9  (Output Page Size)
    EOR = b"\x19"  # 25 (End of Record Option)
    TTYPE = b"\x18"  # 24 (Terminal Type)
    NAWS = b"\x1f"  # 31 (Negotiate About Window Size)
    TSPEED = b"\x20"  # 32 (Terminal Speed)
    LFLOW = b"\x21"  # 33 (Remote Flow Control)
    LINEMODE = b"\x22"  # 34 (Line mode)
    XDISPLOC = b"\x23"  # 35 (X Display Location)
    OLD_ENVIRON = b"\x24"  # 36 (Environment Option)
    NEW_ENVIRON = b"\x27"  # 39 (New Environment Option)


class TelnetClient:
    """
    Telnet Protocol Wrapper di atas Socket Engine.
    Terintegrasi dengan TelnetCmd & TelnetOpt untuk kontrol granular dan Type-Safety.
    """

    def __init__(self, host: str, port: int = 23, timeout: float = 10.0, **kwargs):
        """Open koneksi Telnet di atas TCP Socket"""
        self.sock = Socket(
            host=host, port=port, protocol="tcp", timeout=timeout, **kwargs
        )
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
                # Escaped IAC (\xff\xff)
                if i + 1 < length and data[i + 1 : i + 2] == TelnetCmd.IAC:
                    clean_data.append(255)
                    i += 2
                    continue

                if i + 1 >= length:
                    self._iac_fragment = data[i:]
                    break

                cmd = data[i + 1 : i + 2]

                # Command Negosiasi (DO, DONT, WILL, WONT) - 3 Bytes
                if cmd in (TelnetCmd.DO, TelnetCmd.DONT, TelnetCmd.WILL, TelnetCmd.WONT):
                    if i + 2 >= length:
                        self._iac_fragment = data[i:]
                        break

                    opt = data[i + 2 : i + 3]

                    # Auto-Rejection / Hardened Fallback
                    # Menolak semua Opsi agar server memberikan pure Plain Text
                    if cmd in (TelnetCmd.DO, TelnetCmd.DONT):
                        self.sock.send(
                            TelnetCmd.IAC + TelnetCmd.WONT + opt
                        )
                    elif cmd in (TelnetCmd.WILL, TelnetCmd.WONT):
                        self.sock.send(
                            TelnetCmd.IAC + TelnetCmd.DONT + opt
                        )

                    i += 3

                # Subnegotiation Block (SB ... SE)
                elif cmd == TelnetCmd.SB:
                    end_sb = data.find(TelnetCmd.IAC + TelnetCmd.SE, i)
                    if end_sb == -1:
                        self._iac_fragment = data[i:]
                        break
                    else:
                        i = end_sb + 2

                # Command Eksekusi (2 Bytes)
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

                # Unknown Command (Safety Skip)
                else:
                    i += 2
            else:
                clean_data.append(data[i])
                i += 1

        return bytes(clean_data)

    def read(
        self,
        expected: Union[str, bytes],
        timeout: Optional[float] = None,
        raw: bool = False,
    ) -> Union[str, bytes]:
        """Melihat Response Telnet"""
        if isinstance(expected, str):
            expected = expected.encode("utf-8")

        wait_time = timeout or self.timeout
        start_time = time.time()

        while (time.time() - start_time) < wait_time:
            if expected in self._buffer:
                idx = self._buffer.find(expected) + len(expected)
                result = self._buffer[:idx]
                self._buffer = self._buffer[idx:]

                return result if raw else result.decode("utf-8", errors="ignore")

            resp = self.sock.recv(readsize=4096)

            if not resp.status and not resp.raw_bytes:
                break

            if resp.raw_bytes:
                clean_chunk = self._negotiate_iac(resp.raw_bytes)
                self._buffer += clean_chunk

            time.sleep(0.05)

        res = self._buffer
        self._buffer = b""
        return res if raw else res.decode("utf-8", errors="ignore")

    def send(
        self,
        command: Union[str, bytes],
        expected: Union[str, bytes],
        timeout: Optional[float] = None,
        raw: bool = False,
    ) -> Union[str, bytes]:
        """Mengirim data Telnet"""
        if isinstance(command, str):
            cmd_payload = f"{command}\r\n".encode("utf-8")
        else:
            cmd_payload = command + b"\r\n"

        self.sock.send(cmd_payload)
        return self.read(expected, timeout, raw)

    def close(self):
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
