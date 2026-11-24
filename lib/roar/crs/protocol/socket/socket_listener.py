import os

from .state_build import IPCPayloadBuilder
from .state_listen import ListenState
from .response import SocketResponse
from .socket_opt_listen import ListenOptions
from .socket_re_listen import ListenResolv
from .socket_fd import ListenFD
from .validate import parse_flags, parse_addr
from ...endpoint import CRS


class ClientListener(
    ListenState,
    ListenResolv,
    ListenOptions,
    ListenFD,
):
    """Special Class to handle IO/Close Listener"""

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
            state=self.state,
            cfd=self._cfd,
            data=data,
            flag=flags,
            mode="sendall",
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
            state=self.state,
            cfd=self._cfd,
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
            state=self.state,
            cfd=self._cfd,
            buffer=buffer,
            flag=flags,
            mode="recv",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def sendto(
        self,
        data: bytes,
        address: tuple[str, int],
        flags: int | None = None,
        **kwargs,
    ) -> SocketResponse:
        """Send datagram along with Host & Port"""
        self._ensure_open("sendto")
        host, port, _, _ = parse_addr(address)
        if flags is not None:
            flags = parse_flags(flags)

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
            state=self.state,
            cfd=self._cfd,
            buffer=buffer,
            flag=flags,
            mode="recvfrom",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

    def shutdown(
        self,
        how: int,
        **kwargs,
    ) -> None:
        """Closing read/write"""
        self._ensure_open("shutdown")
        packet = IPCPayloadBuilder.build(
            state=self.state,
            cfd=self._cfd,
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
        Disconnecting Client Listener

        Closing Golang FD Client `close()`
        Closing Golang and Python FD Client `close(fileno)`
        """
        if self._is_closed_cfd:
            raise OSError("ClientFD has been closed")

        def closefd(val) -> None:
            if isinstance(val, bool):
                return None
            if not isinstance(val, int):
                return None
            if val < 0:
                return None
            if not val == self.state._client_fd:
                return None
            self.state._client_fd = -1
            try:
                return os.close(val)
            except OSError:
                return None

        if fileno is not None:
            closefd(fileno)

        packet = IPCPayloadBuilder.build(
            state=self.state,
            cfd=self._cfd,
            mode="close-cfd",
        )

        CRS.send(packet)
        self._is_closed_cfd = True
        return None
