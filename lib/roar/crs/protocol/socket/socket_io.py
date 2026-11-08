from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .validate import is_tuple2
from ...endpoint import CRS


class SocketIO:
    """Daftar semua socket IO"""

    def sendall(
        self,
        data: str | bytes,
        flags: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Sending all data"""
        self._ensure_open("sendall")
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
        data: str | bytes,
        flags: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Sending data"""
        self._ensure_open("send")
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
        flags: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Taking Buffer"""
        self._ensure_open("recv")
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
        data: str | bytes,
        host: str | tuple[str, str | int],
        port: str | int = None,
        flags: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Send datagram along with Host & Port"""
        self._ensure_open("sendto")
        if is_tuple2(host):
            host, port = host

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
        flags: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Taking Buffer"""
        self._ensure_open("recvfrom")
        packet = IPCPayloadBuilder.build(
            state=self,
            buffer=buffer,
            flag=flags,
            mode="recvfrom",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def sendmsg(
        self,
        buffer: int,
        ancdata: int = None,
        flags: str | int = None,
        host: str | tuple[str, str | int] = None,
        port: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Sending message"""
        self._ensure_open("sendmsg")
        if is_tuple2(host):
            host, port = host

        packet = IPCPayloadBuilder.build(
            state=self,
            buffer=buffer,
            ancdata=ancdata,
            host=host,
            port=port,
            flag=flags,
            mode="sendmsg",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def recvmsg(
        self,
        buffer: int,
        ancdata: int = None,
        flags: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Taking Buffer"""
        self._ensure_open("recvmsg")
        packet = IPCPayloadBuilder.build(
            state=self,
            buffer=buffer,
            ancdata=ancdata,
            flag=flags,
            mode="recvmsg",
        )

        resp = CRS.send(packet)
        res = SocketResponse(resp)
        return res.raw_bytes, res.rmsg, res._flags, res.remote_ip
