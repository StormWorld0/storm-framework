from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .validate import is_tuple2, parse_flags
from ...endpoint import CRS


class SocketResolver:
    """Daftar semua socket resolver"""

    def getaddrinfo(
        self,
        address: tuple[str, str | int],
        family: str | int = None,
        type: str | int = None,
        proto: str | int = None,
        flags: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Dapatkan informasi alamat"""
        self._ensure_open("getaddrinfo")
        if is_tuple2(address):
            host, port = address

        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            addr_fam=family,
            stype=type,
            sproto=proto,
            flag=flags,
            mode="getaddrinfo",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        return response.addrinfo

    def getnameinfo(
        self,
        address: tuple[str, int, int, int],
        flags: int = None,
        **kwargs,
    ) -> SocketResponse:
        """Dapatkan Hostname dari (IP, PORT)"""
        self._ensure_open("getnameinfo")
        if not isinstance(address, tuple):
            raise TypeError("address must be a tuple")
        if len(address) not in (2, 4):
            raise ValueError("Expected 2 or 4 arguments")
            
        host, port = address[:2]
        flowinfo = address[2] if len(address) == 4 else None
        scopeid = address[3] if len(address) == 4 else None
        if flags not None:
            flags = parse_flags(flags)
        
        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            flowinfo=flowinfo,
            scopeid=scopeid,
            flag=flags,
            mode="getnameinfo",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        return response.nameinfo

    def getsockname(self, **kwargs) -> SocketResponse:
        """Dapatkan IP local socket"""
        self._ensure_open("getsockname")
        packet = IPCPayloadBuilder.build(
            state=self,
            mode="getsockname",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        return response.local_ip

    def getpeername(self, **kwargs) -> SocketResponse:
        """Dapatkan IP server socket"""
        self._ensure_open("getpeername")
        packet = IPCPayloadBuilder.build(
            state=self,
            mode="getpeername",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        return response.remote_ip
