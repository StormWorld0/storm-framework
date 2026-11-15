from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .validate import is_tuple2, parse_flags
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

    def getsockname(self, **kwargs) -> SocketResponse:
        """Dapatkan IP local socket"""
        self.state._ensure_open("getsockname")
        packet = IPCPayloadBuilder.build(
            state=self.state,
            mode="getsockname",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        return response.local_ip

    def getpeername(self, **kwargs) -> SocketResponse:
        """Dapatkan IP server socket"""
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
        **kwargs,
    ) -> SocketResponse:
        """Disconnecting"""
        if self.state._is_closed:
            return SocketResponse({"status": "closed", "session_id": self.state.sessid})

        packet = IPCPayloadBuilder.build(state=self.state, mode="close", close_session=True)
        resp = CRS.send(packet)
        self.state._is_closed = True
        return SocketResponse(resp)
        
