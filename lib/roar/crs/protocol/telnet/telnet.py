import time
from typing import Optional, Union
from .network import Socket

class TelnetClient:
    """
    Telnet Protocol Wrapper di atas Socket Engine.
    Menangani Telnet Handshake (IAC) secara otomatis dan menyediakan 
    interface stream berbasis text/prompt untuk modul tingkat tinggi.
    """
    # RFC 854 Telnet Commands
    IAC  = b'\xff' # 255
    DONT = b'\xfe' # 254
    DO   = b'\xfd' # 253
    WONT = b'\xfc' # 252
    WILL = b'\xfb' # 251

    def __init__(self, host: str, port: int = 23, timeout: float = 10.0, **kwargs):
        # Inisialisasi Socket
        self.sock = Socket(
            host=host, 
            port=port, 
            protocol="tcp", 
            timeout=timeout, 
            **kwargs
        )
        self.timeout = timeout
        self._buffer = b""

    def _negotiate_iac(self, raw_data: bytes) -> bytes:
        """
        State machine sederhana untuk filter dan auto-reply Telnet Handshake.
        Memaksa server untuk fallback ke mode plain-text (Dumb Terminal).
        """
        clean_data = bytearray()
        i = 0
        length = len(raw_data)

        while i < length:
            if raw_data[i:i+1] == self.IAC:
                if i + 2 < length:
                    cmd = raw_data[i+1:i+2]
                    opt = raw_data[i+2:i+3]
                    
                    # Otomatis tolak semua opsi (WONT / DONT)
                    # Catatan: payload builder Anda mendukung tipe data `bytes` 
                    # walaupun type-hint Socket.send adalah `str`.
                    if cmd in (self.DO, self.DONT):
                        self.sock.send(self.IAC + self.WONT + opt, mode="send_only")
                    elif cmd in (self.WILL, self.WONT):
                        self.sock.send(self.IAC + self.DONT + opt, mode="send_only")
                    
                    i += 3 # Skip 3 bytes (IAC + CMD + OPT)
                else:
                    # Incomplete IAC di ujung stream, kita anggap sampah/abaikan 
                    # untuk implementasi sederhana ini
                    i += 1 
            else:
                clean_data.append(raw_data[i])
                i += 1

        return bytes(clean_data)

    def read_until(self, expected: Union[str, bytes], timeout: Optional[float] = None) -> str:
        """
        Membaca stream secara dinamis sampai menemukan pola prompt tertentu
        (misal: 'Username:', 'Password:', atau 'Router#').
        """
        if isinstance(expected, str):
            expected = expected.encode('utf-8')

        wait_time = timeout or self.timeout
        start_time = time.time()

        while (time.time() - start_time) < wait_time:
            if expected in self._buffer:
                # Pola ditemukan, potong buffer
                idx = self._buffer.find(expected) + len(expected)
                result = self._buffer[:idx]
                self._buffer = self._buffer[idx:] # Simpan sisa data di buffer
                return result.decode('utf-8', errors='ignore')

            # Ambil data baru dari Socket
            resp = self.sock.recv(readsize=4096)
            
            if not resp.status and not resp.raw_bytes:
                # Koneksi putus atau EOF
                break

            if resp.raw_bytes:
                # Filter IAC Handshake sebelum masuk buffer
                clean_chunk = self._negotiate_iac(resp.raw_bytes)
                self._buffer += clean_chunk
            
            time.sleep(0.05) # Mencegah CPU Spiking

        # Timeout tercapai, kembalikan apa yang ada
        res = self._buffer
        self._buffer = b""
        return res.decode('utf-8', errors='ignore')

        def execute(self, command: Union[str, bytes], expect_prompt: Union[str, bytes], timeout: Optional[float] = None) -> str:
        """
        Menerima command baik dalam bentuk string maupun raw bytes.
        Sangat berguna jika ada modul yang ingin mengirim eksploit binary via Telnet.
        """
        if isinstance(command, str):
            cmd_payload = f"{command}\r\n".encode('utf-8')
        else:
            # Jika user mengirim bytes murni, cukup menambahkan CRLF bytes
            cmd_payload = command + b"\r\n"
            
        self.sock.send(cmd_payload) 
        return self.read_until(expect_prompt, timeout)

    def close(self):
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
              
