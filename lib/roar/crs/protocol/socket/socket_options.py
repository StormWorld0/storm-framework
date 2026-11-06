from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from ...endpoint import CRS


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
        return SocketResponse(resp)

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
        val = response._data.get("val_opt", -1)
        return val

    def settimeout(self, value: float | int):
        """Global Timeout"""
        if not isinstance(value, (float, int)):
            raise ValueError("'settimeout' Argument must be a float or int.")
        self._timeout = float(value)
        return self

    def gettimeout(self) -> float:
        """Taking a timeout"""
        if self._timeout == 0.0:
            value = None
        if self._timeout != 0.0:
            value = self._timeout
        return value
