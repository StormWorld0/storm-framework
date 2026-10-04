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
            infotls=False,
            mode="getaddrinfo",
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response
