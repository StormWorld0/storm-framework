from .socket_listener import ClientListener
from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .validate import is_tuple2
from ...endpoint import CRS
from typing import Self
from lib.smf.exception import SocketError


class SocketCore:
    """Daftar semua fungsi core socket"""

    def socket(
        self,
        af: str | int,
        type: str | int,
        proto: str | int = None,
        **kwargs,
    ) -> Self:
        """Open Socket"""
        self._ensure_open("socket")
        self.family = af
        self.type = type
        self.proto = proto if proto is not None else 0
        packet = IPCPayloadBuilder.build(
            state=self,
            addr_fam=af,
            stype=type,
            sproto=proto,
            mode="socket",
        )

        resp = SocketResponse(CRS.send(packet))
        if not resp.ok:
            raise SocketError(f"Socket creation failed: {resp.message}")
        return self

    def bind(
        self,
        address: tuple[str, str | int],
        **kwargs,
    ) -> SocketResponse:
        """Binding local connection"""
        self._ensure_open("bind")
        if is_tuple2(address):
            host, port = address

        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            mode="bind",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

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
        return SocketResponse(resp)

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

        cfd = response._client_fd()
        if cfd < 0:
            return None, response
        return ClientListener(self, cfd), response

    def connect(
        self,
        address: tuple[str, str | int],
        **kwargs,
    ) -> SocketResponse:
        """Open Connection"""
        self._ensure_open("connect")
        if is_tuple2(address):
            host, port = address

        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            mode="connect",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def create_connection(
        self,
        address: tuple[str, str | int],
        timeout: float | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Creating a TCP Stream connection"""
        self._ensure_open("create")
        self.family = 2  # Keep default AF_INET
        self.type = 1  # Keep default SOCK_STREAM
        self.proto = 0  # Keep default Kernel
        if is_tuple2(address):
            host, port = address

        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            timeout=timeout,
            mode="create",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def detach(self) -> int:
        """Take over the FD socket"""
        value = -1
        if self._sock_fd == -1:
            value = self.fileno()
            self._sock_fd = -1
            self.close()
            return value
        else:
            value = self._sock_fd
            self._sock_fd = -1
            self.close()

        if value == -1:
            raise ValueError("No FD, run 'socket' first before taking over FD.")
        return value

    def shutdown(
        self,
        how: str | int,
        **kwargs,
    ) -> SocketResponse:
        """Closing read/write"""
        self._ensure_open("shutdown")
        packet = IPCPayloadBuilder.build(
            state=self,
            how=how,
            mode="shutdown",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def close(
        self,
        **kwargs,
    ) -> SocketResponse:
        """Disconnecting"""
        if self._is_closed:
            return SocketResponse({"status": "closed", "session_id": self.sessid})

        packet = IPCPayloadBuilder.build(state=self, mode="close", close_session=True)
        resp = CRS.send(packet)
        self._is_closed = True
        return SocketResponse(resp)
