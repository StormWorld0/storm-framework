from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .validate import is_tuple2
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
        address: tuple[str, str | int],
        flags: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Dapatkan Hostname dari (IP, PORT)"""
        self._ensure_open("getnameinfo")
        if is_tuple2(address):
            host, port = address

        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
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
