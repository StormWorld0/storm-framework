from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from ...transport import CRS


class SocketResolver:
    """Daftar semua socket resolver"""

    def getaddrinfo(
        self,
        host: str | tuple[str, str | int],
        port: str | int = None,
        addrf: str | int = None,
        stype: str | int = None,
        sproto: str | int = None,
        flag: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Dapatkan informasi alamat"""
        self._ensure_open("getaddrinfo")
        if isinstance(host, tuple):
            if len(host) != 2:
                raise ValueError("Host tuple only accepts 2 elements: (host, port)")
            host, port = host
            
        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            addr_fam=addrf,
            stype=stype,
            sproto=sproto,
            flag=flag,
            mode="getaddrinfo",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response.addrinfo

    def getnameinfo(
        self,
        host: str | tuple[str, str | int],
        port: str | int = None,
        flag: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Dapatkan Hostname dari IP:PORT"""
        self._ensure_open("getnameinfo")
        if isinstance(host, tuple):
            if len(host) != 2:
                raise ValueError("Host tuple only accepts 2 elements: (host, port)")
            host, port = host
            
        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            flag=flag,
            mode="getnameinfo",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
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
        response._trace()
        response._ktrace()
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
        response._trace()
        response._ktrace()
        return response.remote_ip
