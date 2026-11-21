import os

from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .utils_fd import real_fd
from ...endpoint import CRS


class ListenFD:
    """Special class instance from Accept function"""

    def fileno(self, **kwargs) -> int:
        """Retrieving FD Client Socket"""
        self._ensure_open("fileno")
        if self.state._client_fd != -1:
            return self.state._client_fd

        packet = IPCPayloadBuilder.build(
            state=self.state,
            cfd=self._cfd,
            mode="fileno-clt",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)

        if uds := response._data.get("client_uds"):
            fd = real_fd(uds)
            self.state._client_fd = fd
            return self.state._client_fd
        return -1

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


class SocketFD:
    """Special class inherited from Socket"""

    def fileno(self, **kwargs) -> int:
        """Taking FD Socket"""
        self._ensure_open("fileno")
        if self._sock_fd != -1:
            return self._sock_fd

        packet = IPCPayloadBuilder.build(
            state=self,
            mode="fileno",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)

        if uds := response._data.get("socket_uds"):
            fd = real_fd(uds)
            self._sock_fd = fd
            return self._sock_fd
        return -1

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
        if not fileno == self._sock_fd:
            return
        self._sock_fd = -1
        return os.close(fileno)
