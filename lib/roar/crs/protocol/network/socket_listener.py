from .state_build import IPCPayloadBuilder
from .response import SocketResponse

from ...transport import CRS


class ClientListener:
    """Class Khusus menangani IO/Close Listener"""

    def __init__(self, cfd: int = None):
        self._cfd = cfd

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
            cfd=self._cfd,
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
            cfd=self._cfd,
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
            cfd=self._cfd,
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
            cfd=self._cfd,
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
            cfd=self._cfd,
            mode="recvfrom",
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def close(
        self,
        **kwargs,
    ) -> SocketResponse:
        """Disconnecting Client Listener"""
        if self._is_closed_cfd:
            return SocketResponse(
                {"status": "WARN", "message": "ClientFD has been closed."}
            )

        packet = IPCPayloadBuilder.build(
            state=self,
            mode="close-cfd",
            close_session=False,
        )

        resp = CRS.send(packet)
        self._is_closed_cfd = True

        response = SocketResponse(resp)
        response._trace()
        return response
