import os

from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .validate import parse_flags
from ...endpoint import CRS


class ObjectTLS:
    """Collection of objects inherited from uptls()"""

    def __init__(self, state):
        self.state = state

    def sendall(
        self,
        data: bytes,
        flags: int | None = None,
        **kwargs,
    ) -> SocketResponse:
        """Sending all data"""
        self.state._ensure_open("sendall")
        if flags is not None:
            flags = parse_flags(flags)

        packet = IPCPayloadBuilder.build(
            state=self.state,
            data=data,
            flag=flags,
            mode="sendall",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def send(
        self,
        data: bytes,
        flags: int | None = None,
        **kwargs,
    ) -> SocketResponse:
        """Sending data"""
        self.state._ensure_open("send")
        if flags is not None:
            flags = parse_flags(flags)

        packet = IPCPayloadBuilder.build(
            state=self.state,
            data=data,
            flag=flags,
            mode="send",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def recv(
        self,
        buffer: int,
        flags: int | None = None,
        **kwargs,
    ) -> SocketResponse:
        """Taking Buffer"""
        self.state._ensure_open("recv")
        if flags is not None:
            flags = parse_flags(flags)

        packet = IPCPayloadBuilder.build(
            state=self.state,
            buffer=buffer,
            flag=flags,
            mode="recv",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def setsockopt(
        self,
        level: int,
        name: int,
        value: int | None = None,
        **kwargs,
    ) -> None:
        """Socket Options Configuration"""
        self.state._ensure_open("setsockopt")
        packet = IPCPayloadBuilder.build(
            state=self.state,
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
        self.state._ensure_open("getsockopt")
        packet = IPCPayloadBuilder.build(
            state=self.state,
            level=level,
            name=name,
            mode="getsockopt",
        )

        resp = CRS.send(packet)
        r = SocketResponse(resp)
        return r._data.get("val_opt", -1)

    def getsockname(self, **kwargs) -> tuple[str, int]:
        """Get local socket IP"""
        self.state._ensure_open("getsockname")
        packet = IPCPayloadBuilder.build(
            state=self.state,
            mode="getsockname",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        return response.local_ip

    def getpeername(self, **kwargs) -> tuple[str, int]:
        """Get socket server IP"""
        self.state._ensure_open("getpeername")
        packet = IPCPayloadBuilder.build(
            state=self.state,
            mode="getpeername",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        return response.remote_ip

    def close(
        self,
        fileno: int | None = None,
        **kwargs,
    ) -> None:
        """
        Disconnecting

        Closing Golang FD `close()`
        Closing Golang and Python FD `close(fileno)`
        """
        if self.state._is_closed:
            raise OSError("The socket is closed")

        def closefd(val) -> None:
            if isinstance(val, bool):
                return None
            if not isinstance(val, int):
                return None
            if val < 0:
                return None
            if not val == self.state._sock_fd:
                return None
            self.state._sock_fd = -1
            try:
                return os.close(val)
            except OSError:
                return None

        if fileno is not None:
            closefd(fileno)

        packet = IPCPayloadBuilder.build(
            state=self.state, mode="close", close_session=True
        )
        CRS.send(packet)
        self.state._is_closed = True
        return None
