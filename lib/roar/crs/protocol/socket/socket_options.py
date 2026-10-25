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
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response

    def getsockopt(
        self,
        level: str | int,
        name: str | int,
        **kwargs,
    ) -> SocketResponse:
        """Mengambil socket options"""
        self._ensure_open("getsockopt")
        packet = IPCPayloadBuilder.build(
            state=self,
            level=level,
            name=name,
            mode="getsockopt",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        val = response._data.get("val_opt", -1)
        return val

    def timeout(self, value: float):
        """Global Timeout"""
        self._timeout = float(value)
        return self

    def goroutine(self, value: int):
        """Global Goroutine"""
        if not isinstance(value, int):
            raise TypeError("[!] Goroutine must be integer.")
        self.con = value
        return self
