from .socket_listener import ClientListener
from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .validate import is_tuple2

from ...transport import CRS


class SocketCore:
    """Daftar semua fungsi core socket"""

    def socket(
        self,
        af: str | int,
        type: str | int,
        proto: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Open Socket"""
        self._ensure_open("socket")
        packet = IPCPayloadBuilder.build(
            state=self,
            addr_fam=af,
            stype=type,
            sproto=proto,
            mode="socket",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response

    def bind(
        self,
        host: str | tuple[str, str | int],
        port: str | int,
        **kwargs,
    ) -> SocketResponse:
        """Binding local connection"""
        self._ensure_open("bind")
        if is_tuple2(host):
            host, port = host
            
        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            mode="bind",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response

    def listen(
        self,
        backlog: int,
        **kwargs,
    ) -> SocketResponse:
        """Waiting for incoming connection"""
        self._ensure_open("listen")
        packet = IPCPayloadBuilder.build(
            state=self,
            backlog=backlog,
            mode="listen",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response

    def accept(
        self,
        **kwargs,
    ) -> SocketResponse:
        """Retrieving Incoming Connections"""
        self._ensure_open("accept")
        packet = IPCPayloadBuilder.build(
            state=self,
            mode="accept",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()

        cfd = response._client_fd()
        if cfd < 0:
            return None, response
        return ClientListener(self, cfd), response

    def connect(
        self,
        host: str | tuple[str, str | int],
        port: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Open Connection"""
        self._ensure_open("connect")
        if is_tuple2(host):
            host, port = host
            
        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            mode="connect",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response

    def create_connection(
        self,
        host: str | tuple[str, str | int],
        port: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Creating a TCP Stream connection"""
        self._ensure_open("create")
        if is_tuple2(host):
            host, port = host
            
        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            mode="create",
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
        """Disconnecting"""
        if self._is_closed:
            return SocketResponse(
                {"status": "already_closed", "session_id": self.sessid, "data": {}}
            )

        packet = IPCPayloadBuilder.build(state=self, mode="close", close_session=True)
        resp = CRS.send(packet)
        self._is_closed = True

        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response
