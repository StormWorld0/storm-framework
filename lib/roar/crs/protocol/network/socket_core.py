from .state_build import IPCPayloadBuilder
from .response import SocketResponse

from ...transport import CRS


class SocketCore:
    """Daftar semua fungsi core socket"""

    def socket(
        self,
        addrf: str | int,
        stype: str | int,
        sproto: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Open Socket"""
        self._ensure_open("socket")
        packet = IPCPayloadBuilder.build(
            state=self,
            addr_fam=addrf,
            stype=stype,
            sproto=sproto,
            mode="socket",
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def bind(
        self,
        host: str,
        port: str | int,
        **kwargs,
    ) -> SocketResponse:
        """Binding local connection"""
        self._ensure_open("bind")
        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            mode="bind",
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
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
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
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
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def connect(
        self,
        host: str,
        port: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Open Connection"""
        self._ensure_open("connect")
        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            mode="connect",
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def create_connection(
        self,
        host: str,
        port: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Creating a TCP Stream connection"""
        self._ensure_open("create")
        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            mode="create",
            infotls=False,
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
        return response
