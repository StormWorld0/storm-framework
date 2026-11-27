import os

from .socket_listener import ClientListener
from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .validate import parse_addr
from .utils_fd import build_uds
from ...endpoint import CRS
from typing import Self
from lib.smf.exception import SocketError


class SocketCore:
    """List of all core socket functions"""

    def socket(
        self,
        family: int,
        type: int,
        proto: int | None = None,
        fileno: str | None = None,
        **kwargs,
    ) -> Self:
        """Open Socket"""
        self._ensure_open("socket")
        self.family = family
        self.type = type
        self.proto = proto if proto is not None else 0
        uds = None
        if fileno is not None:
            uds = build_uds(fileno)

        packet = IPCPayloadBuilder.build(
            state=self,
            addr_fam=family,
            stype=type,
            sproto=proto,
            fileno=uds,
            mode="socket",
        )

        resp = SocketResponse(CRS.send(packet))
        if not resp.ok:
            raise SocketError(resp.message)
        return self

    def bind(
        self,
        address: tuple[str, int],
        **kwargs,
    ) -> None:
        """Binding local connection"""
        self._ensure_open("bind")
        host, port, _, _ = parse_addr(address)

        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            mode="bind",
        )

        CRS.send(packet)
        return None

    def listen(
        self,
        backlog: int,
        **kwargs,
    ) -> None:
        """Waiting for incoming connection"""
        self._ensure_open("listen")
        packet = IPCPayloadBuilder.build(
            state=self,
            backlog=backlog,
            mode="listen",
        )

        resp = CRS.send(packet)
        return None

    def accept(
        self,
        **kwargs,
    ) -> tuple[object, tuple[str, int]] | None:
        """Retrieving Incoming Connections"""
        self._ensure_open("accept")
        packet = IPCPayloadBuilder.build(
            state=self,
            mode="accept",
        )

        resp = CRS.send(packet)
        r = SocketResponse(resp)

        cfd = r._client_fd()
        if cfd < 0:
            return None, None
        return ClientListener(self, cfd), r.remote_ip

    def connect(
        self,
        address: tuple[str, int],
        **kwargs,
    ) -> None:
        """Open Connection"""
        self._ensure_open("connect")
        host, port, _, _ = parse_addr(address)

        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            mode="connect",
        )

        CRS.send(packet)
        return None

    def create_connection(
        self,
        address: tuple[str, int],
        timeout: float | int | None = None,
        **kwargs,
    ) -> Self:
        """Creating a TCP Stream connection"""
        self._ensure_open("create")
        self.family = 2  # Keep default AF_INET
        self.type = 1  # Keep default SOCK_STREAM
        self.proto = 0  # Keep default Kernel
        host, port, _, _ = parse_addr(address)

        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            timeout=timeout,
            mode="create",
        )

        CRS.send(packet)
        return self

    def detach(self) -> int:
        """
        Take over the FD socket
        change ownership of Python FD
        and automatically close Golang FD!
        """
        if self._sock_fd == -1:
            value = self.fileno()
        else:
            value = self._sock_fd

        self._sock_fd = -1
        self.close()

        if value == -1:
            raise ValueError("No FD, run 'socket' first before taking over FD.")
        return value

    def shutdown(
        self,
        how: int,
        **kwargs,
    ) -> None:
        """Closing read/write"""
        self._ensure_open("shutdown")
        packet = IPCPayloadBuilder.build(
            state=self,
            how=how,
            mode="shutdown",
        )

        CRS.send(packet)
        return None

    def close(
        self,
        fileno: int | None = None,
        **kwargs,
    ) -> None:
        """
        Disconnecting

        Closing Golang FD `close()`
        Closing Golang and Python FD `close(fileno)`

        Note: Once called, it cannot be called again.
        If you previously used `close()` and the Python FD is still active,
        close it manually with `os.close(fileno)`.
        """
        if self._is_closed:
            return OSError("The socket is closed")

        def closefd(val) -> None:
            if isinstance(val, bool):
                return None
            if not isinstance(val, int):
                return None
            if val < 0:
                return None
            if not val == self._sock_fd:
                return None
            self._sock_fd = -1
            try:
                return os.close(val)
            except OSError:
                return None

        if fileno is not None:
            closefd(fileno)

        packet = IPCPayloadBuilder.build(state=self, mode="close", close_session=True)
        CRS.send(packet)
        self._is_closed = True
        return None
