from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from ...endpoint import CRS


class ListenInspect:
    """Class khusus menangani Inspector Listener"""

    def setsockopt(
        self,
        level: str | int,
        name: str | int,
        value: int = None,
        **kwargs,
    ) -> SocketResponse:
        """Socket Options Configuration"""
        self.state._ensure_open("setsockopt")
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
        level: str | int,
        name: str | int,
        **kwargs,
    ) -> SocketResponse:
        """Mengambil socket options"""
        self.state._ensure_open("getsockopt")
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

    def getsockname(self) -> SocketResponse:
        """Dapatkan IP local socket"""
        self.state._ensure_open("getsockname")
        packet = IPCPayloadBuilder.build(
            state=self,
            cfd=self._cfd,
            mode="getsockname",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        return response.local_ip

    def getpeername(self) -> SocketResponse:
        """Dapatkan IP server socket"""
        self.state._ensure_open("getpeername")
        packet = IPCPayloadBuilder.build(
            state=self,
            cfd=self._cfd,
            mode="getpeername",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        return response.remote_ip

    def settimeout(self, value: float | int):
        """Global Timeout"""
        self.state._timeout = float(value)
        return self

    
