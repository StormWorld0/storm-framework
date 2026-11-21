import os

from .state_build import IPCPayloadBuilder
from .state_listen import ListenState
from .response import SocketResponse
from .socket_re_listen import ListenResolv
from .socket_fd import ListenFD
from .validate import parse_flags, parse_addr
from ...endpoint import CRS


class ClientListener(ListenState, ListenResolv, ListenFD):
    """Class Khusus menangani IO/Close Listener"""

    def sendall(
        self,
        data: bytes,
        flags: int | None = None,
        **kwargs,
    ) -> SocketResponse:
        """Sending all data"""
        self.state._ensure_open("sendall")
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
        self.state._ensure_open("send")
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
        self.state._ensure_open("recv")
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
        self.state._ensure_open("sendto")
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
        self.state._ensure_open("recvfrom")
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
        how: str | int,
        **kwargs,
    ) -> SocketResponse:
        """Closing read/write"""
        self.state._ensure_open("shutdown")
        self._ensure_open("shutdown")

        packet = IPCPayloadBuilder.build(
            state=self,
            cfd=self._cfd,
            how=how,
            mode="shutdown",
        )

        resp = CRS.send(packet)
        return SocketResponse(resp)

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
            cfd=self._cfd,
            mode="close-cfd",
        )

        resp = CRS.send(packet)
        self._is_closed_cfd = True
        return SocketResponse(resp)

    def closefd(
        self,
        fileno: int,
        **kwargs,
    ) -> None:
        """Closing the Python table socket FD"""
        if isinstance(fileno, bool):
            raise TypeError("'closefd' does not support Boolean")
        if not isinstance(fileno, int):
            raise TypeError("'closefd' only supports int")
        if fileno <= 0:
            raise ValueError(f"'closefd' invalid value {fileno}")
        if not fileno == self.state._client_fd:
            return
        self.state._client_fd = -1
        return os.close(fileno)
