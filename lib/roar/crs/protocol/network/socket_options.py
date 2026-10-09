from .state_build import IPCPayloadBuilder
from .response import SocketResponse

from ...transport import CRS


class SocketOptions:
    """Daftar semua socket options"""

    def setsockopt(
        self,
        level: str | int,
        name: str | int,
        value: int = None,
        **kwargs,
    ) -> SocketResponse:
        """Socket Options Configuration"""
        self._ensure_open("setsockopt")
        packet = IPCPayloadBuilder.build(
            state=self,
            level=level,
            name=name,
            value=value,
            mode="setsockopt",
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def timeout(self, value: float):
        """Global Timeout"""
        return self._timeout = value

    def goroutine(self, con: int):
        """Global Goroutine"""
        if not isinstance(con, int):
            raise TypeError("[!] Goroutine must be integer.")
        return self.con = con
