from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from ...endpoint import CRS


class ListenOptions:
    """List all listener options"""

    def setsockopt(
        self,
        level: int,
        name: int,
        value: int | None = None,
        **kwargs,
    ) -> SocketResponse:
        """Socket Options Configuration"""
        self._ensure_open("setsockopt")
        packet = IPCPayloadBuilder.build(
            state=self,
            cfd=self._cfd,
            level=level,
            name=name,
            value=value,
            mode="setsockopt",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def getsockopt(
        self,
        level: int,
        name: int,
        **kwargs,
    ) -> int:
        """Getting socket options"""
        self._ensure_open("getsockopt")
        packet = IPCPayloadBuilder.build(
            state=self,
            cfd=self._cfd,
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
        self._ensure_open("settimeout")
        if isinstance(value, bool):
            raise TypeError("'settimeout' does not support boolean")
        if not isinstance(value, (float, int)):
            raise TypeError("'settimeout' only supports float or int.")
        self.state._timeout = float(value)
        return self

    def gettimeout(self) -> float | None:
        """Taking a timeout"""
        self._ensure_open("gettimeout")
        value = None
        if self.state._timeout != 0.0:
            value = self.state._timeout
        return value
