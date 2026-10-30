from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .utils_fd import real_fd
from ...transport import CRS


class ListenFD:
    """Class khusus inheritance dari fungsi Accept"""

    def fileno(self, **kwargs) -> int:
        """Mengambil File-Decriptor milik Client Socket"""
        self.state._ensure_open("fileno")
        if self.state._client_fd != -1:
            return self.state._client_fd

        packet = IPCPayloadBuilder.build(
            state=self.state,
            cfd=self._cfd,
            mode="fileno-clt",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()

        if uds := response._data.get("client_uds"):
            fd = real_fd(uds)
            self.state._client_fd = fd
            return self.state._client_fd
        return -1


class SocketFD:
    """Class khusus inheritance dari Socket"""

    def fileno(self, **kwargs) -> int:
        """Mengambil File-Decriptor milik Socket"""
        self._ensure_open("fileno")
        if self._sock_fd != -1:
            return self._sock_fd

        packet = IPCPayloadBuilder.build(
            state=self,
            mode="fileno",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()

        if uds := response._data.get("uds_path"):
            fd = real_fd(uds)
            self._sock_fd = fd
            return self._sock_fd
        return -1
