from .config import TelnetCmd


class TelnetIAC:
    """Mengelola logika IAC"""

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
