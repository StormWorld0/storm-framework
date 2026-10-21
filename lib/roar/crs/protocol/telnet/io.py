import time
from .config import TelnetCmd
from typing import Union, List, Tuple


class TelnetIO:
    """Logika I/O"""

    def read(
        self,
        expected: Union[str, bytes, List[Union[str, bytes]]] = b"",
    ) -> Tuple[Union[str, bytes], int]:
        """Membaca Response Telnet (Tuple return: data, match_index)"""
        self._ensure_open("read")
        
        timeout = self._timeout
        raw = self.raw

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

        wait_time = timeout if timeout is not None else self.timeout
        start_time = time.time()

        while True:
            if expected_bytes:
                for idx, exp in enumerate(expected_bytes):
                    if exp in self._buffer:
                        pos = self._buffer.find(exp) + len(exp)
                        result = self._buffer[:pos]
                        self._buffer = self._buffer[pos:]
                        return (
                            result if raw else result.decode("utf-8", errors="ignore")
                        ), idx

            if (time.time() - start_time) >= wait_time:
                break

            read_timeout = 0.8 if self._buffer else wait_time

            # Memperbaiki state checker: Evaluasi status koneksi keseluruhan (resp_con), bukan variabel independen.
            if self.resp_con.ok:
                resp = self.sock.timeout(read_timeout).recv(readsize=4096)

                if resp.status in ("ERROR", "WARN"):
                    break

                if resp.ok and not resp.raw_bytes:
                    if self._buffer:
                        break
                    continue

                clean_chunk = self._negotiate_iac(resp.raw_bytes)
                self._buffer += clean_chunk

                if not expected_bytes:
                    break
            else:
                break

        res = self._buffer
        self._buffer = b""
        response = res if raw else res.decode("utf-8", errors="ignore")
        return response, -1

    def send(
        self,
        command: Union[str, bytes],
        expected: Union[str, bytes, List[Union[str, bytes]]] = b"",
    ) -> Tuple[Union[str, bytes], int]:
        """Mengirim data Telnet dan langsung membaca Response"""
        self._ensure_open("send")
        
        # Mencegah payload biner (negosiasi IAC) rusak akibat penambahan CRLF otomatis
        if isinstance(command, str):
            cmd_payload = f"{command}\r\n".encode("utf-8")
        else:
            # Jika diawali dengan byte IAC, asumsikan ini adalah perintah protokol murni
            if command.startswith(TelnetCmd.IAC):
                cmd_payload = command
            else:
                cmd_payload = command + b"\r\n"

        # Validasi pengiriman. Jika socket drop, gagalkan langsung tanpa menunggu siklus read.
        send_status = self.sock.timeout(self._timeout).send(cmd_payload)
        if not send_status.ok:
            return (b"" if self.raw else ""), -1

        return self.read(expected, self._timeout, self.raw)
