from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .socket_inspector import Inspector
from .validate import is_tuple2
from ...transport import CRS


class ClientListener(Inspector):
    """Class Khusus menangani IO/Close Listener"""

    def __init__(self, state, cfd: int = None):
        self.state = state
        self._cfd = cfd
        self._is_closed_cfd = False

    def sendall(
        self,
        data: str | bytes,
        flags: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Sending all data"""
        self.state._ensure_open("sendall")
        packet = IPCPayloadBuilder.build(
            state=self.state,
            cfd=self._cfd,
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
        self.state._ensure_open("send")
        packet = IPCPayloadBuilder.build(
            state=self.state,
            cfd=self._cfd,
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
        readsize: int = None,
        flags: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Taking Buffer"""
        self.state._ensure_open("recv")
        packet = IPCPayloadBuilder.build(
            state=self.state,
            cfd=self._cfd,
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
        self.state._ensure_open("sendto")
        if is_tuple(host):
            host, port = host

        packet = IPCPayloadBuilder.build(
            state=self.state,
            cfd=self._cfd,
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
        self.state._ensure_open("recvfrom")
        if is_tuple2(host):
            host, port = host

        packet = IPCPayloadBuilder.build(
            state=self.state,
            cfd=self._cfd,
            readsize=readsize,
            flag=flags,
            mode="recvfrom",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
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
            state=self.state,
            mode="close-cfd",
        )

        resp = CRS.send(packet)
        self._is_closed_cfd = True

        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response
