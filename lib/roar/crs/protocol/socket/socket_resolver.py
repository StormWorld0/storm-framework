from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from ...transport import CRS


class SocketResolver:
    """Daftar semua socket resolver"""

    def getaddrinfo(
        self,
        host: str,
        port: str | int,
        addrf: str | int = None,
        stype: str | int = None,
        sproto: str | int = None,
        flag: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Dapatkan informasi alamat"""
        self._ensure_open("getaddrinfo")
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

    def getsockname(self, **kwargs):
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

    def getpeername(self, **kwargs):
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
