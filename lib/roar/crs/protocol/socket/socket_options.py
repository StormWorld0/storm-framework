from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from ...endpoint import CRS
from typing import Self


class SocketOptions:
    """List all socket options"""

    def setsockopt(
        self,
        level: int,
        name: int,
        value: int | None = None,
        **kwargs,
    ) -> None:
        """Socket Options Configuration"""
        self._ensure_open("setsockopt")
        packet = IPCPayloadBuilder.build(
            state=self,
            level=level,
            name=name,
            value=value,
            mode="setsockopt",
        )

        CRS.send(packet)
        return None

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
            level=level,
            name=name,
            mode="getsockopt",
        )

        resp = CRS.send(packet)
        r = SocketResponse(resp)
        return r._data.get("val_opt", -1)

    def settimeout(self, value: float | int) -> Self:
        """Global Timeout"""
        if isinstance(value, bool):
            raise TypeError("'settimeout' does not support boolean")
        if not isinstance(value, (float, int)):
            raise TypeError("'settimeout' only supports float or int.")
        self._timeout = float(value)
        return self

    def gettimeout(self) -> float | None:
        """Taking a timeout"""
        return self._timeout
