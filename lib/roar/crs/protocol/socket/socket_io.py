from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .validate import is_tuple2

from ...transport import CRS


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
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response

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
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response

    def recv(
        self,
        readsize: int,
        flags: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Taking Buffer"""
        self._ensure_open("recv")
        packet = IPCPayloadBuilder.build(
            state=self,
            readsize=readsize,
            flag=flags,
            mode="recv",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response

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
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response

    def recvfrom(
        self,
        readsize: int,
        host: str | tuple[str, str | int] = None,
        port: str | int = None,
        flags: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Taking Buffer"""
        self._ensure_open("recvfrom")
        if is_tuple2(host):
            host, port = host

        packet = IPCPayloadBuilder.build(
            state=self,
            readsize=readsize,
            host=host,
            port=port,
            flag=flags,
            mode="recvfrom",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response
