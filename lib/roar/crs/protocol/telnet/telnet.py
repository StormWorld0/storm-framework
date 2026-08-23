# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy

import time
from typing import Optional, Union
from ..network.network import Socket

class TelnetClient:
    """
    Telnet Protocol Wrapper (Weaponized Level - RFC 854 Fully Compliant).
    Menangani Telnet Handshake, Subnegotiation, Fragmented TCP, dan semua Opcode standar.
    """
    # RFC 854 Telnet Control Codes
    SE   = b'\xf0' # 240 (Subnegotiation End)
    NOP  = b'\xf1' # 241 (No Operation)
    DM   = b'\xf2' # 242 (Data Mark)
    BRK  = b'\xf3' # 243 (Break)
    IP   = b'\xf4' # 244 (Interrupt Process)
    AO   = b'\xf5' # 245 (Abort Output)
    AYT  = b'\xf6' # 246 (Are You There)
    EC   = b'\xf7' # 247 (Erase Character)
    EL   = b'\xf8' # 248 (Erase Line)
    GA   = b'\xf9' # 249 (Go Ahead)
    SB   = b'\xfa' # 250 (Subnegotiation Begin)
    WILL = b'\xfb' # 251 
    WONT = b'\xfc' # 252 
    DO   = b'\xfd' # 253 
    DONT = b'\xfe' # 254 
    IAC  = b'\xff' # 255 (Interpret As Command)

    def __init__(self, host: str, port: int = 23, timeout: float = 10.0, **kwargs):
        self.sock = Socket(
            host=host, 
            port=port, 
            protocol="tcp", 
            timeout=timeout, 
            **kwargs
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
            if data[i:i+1] == self.IAC:
                # 1. Escaped IAC (\xff\xff -> Data biner 255)
                if i + 1 < length and data[i+1:i+2] == self.IAC:
                    clean_data.append(255)
                    i += 2
                    continue

                if i + 1 >= length:
                    self._iac_fragment = data[i:]
                    break
                
                cmd = data[i+1:i+2]

                # 2. Kasus DO, DONT, WILL, WONT (3 Bytes)
                if cmd in (self.DO, self.DONT, self.WILL, self.WONT):
                    if i + 2 >= length:
                        self._iac_fragment = data[i:]
                        break
                    
                    opt = data[i+2:i+3]
                    
                    if cmd in (self.DO, self.DONT):
                        self.sock.send(self.IAC + self.WONT + opt, mode="send_only")
                    elif cmd in (self.WILL, self.WONT):
                        self.sock.send(self.IAC + self.DONT + opt, mode="send_only")
                    
                    i += 3 

                # 3. Kasus Subnegotiation (IAC SB ... IAC SE)
                elif cmd == self.SB:
                    end_sb = data.find(self.IAC + self.SE, i)
                    if end_sb == -1:
                        self._iac_fragment = data[i:]
                        break
                    else:
                        i = end_sb + 2
                
                # 4. Kasus 2-Byte Commands (NOP, GA, AYT, dll)
                elif cmd in (self.NOP, self.DM, self.BRK, self.IP, self.AO, self.AYT, self.EC, self.EL, self.GA):
                    # Kita bisa drop (ignore) perintah ini agar tidak masuk buffer modul,
                    # atau membalas secara spesifik jika diperlukan di masa depan.
                    i += 2
                
                # 5. Fallback/Unknown IAC Command (Proteksi jika ada opsi RFC tidak standar)
                else:
                    # Mengasumsikan unknown command memiliki panjang 2 bytes
                    i += 2 
            else:
                clean_data.append(data[i])
                i += 1

        return bytes(clean_data)

    def read_until(self, expected: Union[str, bytes], timeout: Optional[float] = None, return_raw: bool = False) -> Union[str, bytes]:
        if isinstance(expected, str):
            expected = expected.encode('utf-8')

        wait_time = timeout or self.timeout
        start_time = time.time()

        while (time.time() - start_time) < wait_time:
            if expected in self._buffer:
                idx = self._buffer.find(expected) + len(expected)
                result = self._buffer[:idx]
                self._buffer = self._buffer[idx:] 
                
                return result if return_raw else result.decode('utf-8', errors='ignore')

            resp = self.sock.recv(readsize=4096)
            
            if not resp.status and not resp.raw_bytes:
                break

            if resp.raw_bytes:
                clean_chunk = self._negotiate_iac(resp.raw_bytes)
                self._buffer += clean_chunk
            
            time.sleep(0.05)

        res = self._buffer
        self._buffer = b""
        return res if return_raw else res.decode('utf-8', errors='ignore')

    def execute(self, command: Union[str, bytes], expect_prompt: Union[str, bytes], timeout: Optional[float] = None, return_raw: bool = False) -> Union[str, bytes]:
        if isinstance(command, str):
            cmd_payload = f"{command}\r\n".encode('utf-8')
        else:
            cmd_payload = command + b"\r\n"
            
        self.sock.send(cmd_payload) 
        return self.read_until(expect_prompt, timeout, return_raw)

    def close(self):
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
                                       
