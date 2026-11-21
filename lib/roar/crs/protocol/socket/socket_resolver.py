from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .validate import is_tuple2, parse_flags, parse_addr
from ...endpoint import CRS


class SocketResolver:
    """Daftar semua socket resolver"""

    def getaddrinfo(
        self,
        address: tuple[str, int],
        family: str | int = None,
        type: str | int = None,
        proto: str | int = None,
        flags: int | None = None,
        **kwargs,
    ) -> SocketResponse:
        """Dapatkan informasi alamat"""
        self._ensure_open("getaddrinfo")
        host, port, _, _ = parse_addr(address)
        if flags is not None:
            flags = parse_flags(flags)

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
        flags: int | None = None,
        **kwargs,
    ) -> SocketResponse:
        """Dapatkan Hostname dari (IP, PORT)"""
        self._ensure_open("getnameinfo")
        host, port, flow, scope = parse_addr(address)
        if flags is not None:
            flags = parse_flags(flags)

        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            flowinfo=flow,
            scopeid=scope,
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
