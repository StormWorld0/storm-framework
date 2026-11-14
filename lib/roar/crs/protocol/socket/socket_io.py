from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .validate import is_tuple2, parse_flags
from ...endpoint import CRS


class SocketIO:
    """Daftar semua socket IO"""

    def sendall(
        self,
        data: bytes,
        flags: int | None = None,
        **kwargs,
    ) -> SocketResponse:
        """Sending all data"""
        self._ensure_open("sendall")
        if flags is not None:
            flags = parse_flags(flags)
            
        packet = IPCPayloadBuilder.build(
            state=self,
            data=data,
            flag=flags,
            mode="sendall",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def sendfile(self, file: str) -> SocketResponse:
        """Sending files"""
        self._ensure_open("sendfile")
        packet = IPCPayloadBuilder.build(
            state=self,
            file=file,
            mode="sendfile",
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
        self._ensure_open("send")
        if flags is not None:
            flags = parse_flags(flags)
            
        packet = IPCPayloadBuilder.build(
            state=self,
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
        self._ensure_open("recv")
        if flags is not None:
            flags = parse_flags(flags)
            
        packet = IPCPayloadBuilder.build(
            state=self,
            buffer=buffer,
            flag=flags,
            mode="recv",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def sendto(
        self,
        data: bytes,
        address: tuple[str, str | int],
        flags: int | None = None,
        **kwargs,
    ) -> SocketResponse:
        """Send datagram along with Host & Port"""
        self._ensure_open("sendto")
        if is_tuple2(address):
            host, port = address
        if flags is not None:
            flags = parse_flags(flags)

        packet = IPCPayloadBuilder.build(
            state=self,
            data=data,
            host=host,
            port=port,
            flag=flags,
            mode="sendto",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def recvfrom(
        self,
        buffer: int,
        flags: int | None = None,
        **kwargs,
    ) -> SocketResponse:
        """Taking Buffer"""
        self._ensure_open("recvfrom")
        if flags is not None:
            flags = parse_flags(flags)
            
        packet = IPCPayloadBuilder.build(
            state=self,
            buffer=buffer,
            flag=flags,
            mode="recvfrom",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)
