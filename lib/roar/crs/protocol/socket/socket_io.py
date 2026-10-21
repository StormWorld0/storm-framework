from .state_build import IPCPayloadBuilder
from .response import SocketResponse

from ...transport import CRS


class SocketIO:
    """Daftar semua socket IO"""

    def sendall(
        self,
        data: str | bytes,
        flag: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Sending all data"""
        self._ensure_open("sendall")
        packet = IPCPayloadBuilder.build(
            state=self,
            data=data,
            flag=flag,
            infotls=False,
            mode="sendall",
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def send(
        self,
        data: str | bytes,
        flag: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Sending data"""
        self._ensure_open("send")
        packet = IPCPayloadBuilder.build(
            state=self,
            data=data,
            flag=flag,
            infotls=False,
            mode="send",
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def recv(
        self,
        readsize: int = None,
        flag: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Taking Buffer"""
        self._ensure_open("recv")
        packet = IPCPayloadBuilder.build(
            state=self,
            readsize=readsize,
            flag=flag,
            infotls=False,
            mode="recv",
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def sendto(
        self,
        data: str | bytes,
        host: str,
        port: str | int = None,
        flag: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Send datagram along with Host & Port"""
        self._ensure_open("sendto")
        packet = IPCPayloadBuilder.build(
            state=self,
            data=data,
            host=host,
            port=port,
            flag=flag,
            infotls=False,
            mode="sendto",
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def recvfrom(
        self,
        readsize: int = None,
        flag: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Taking Buffer"""
        self._ensure_open("recvfrom")
        packet = IPCPayloadBuilder.build(
            state=self,
            readsize=readsize,
            flag=flag,
            infotls=False,
            mode="recvfrom",
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response
