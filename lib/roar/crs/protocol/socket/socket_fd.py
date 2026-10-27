from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .utils_fd import real_fd
from ...transport import CRS


class ListenFD:
    """Class khusus inheritance dari fungsi Accept"""

    def fileno(self, **kwargs) -> int:
        """Mengambil File-Decriptor milik Client Socket"""
        self.state._ensure_open("fileno")
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
            return real_fd(uds)
        return -1


class SocketFD:
    """Class khusus inheritance dari Socket"""

    def fileno(self, **kwargs) -> int:
        """Mengambil File-Decriptor milik Socket"""
        self._ensure_open("fileno")
        packet = IPCPayloadBuilder.build(
            state=self,
            mode="fileno",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        if uds := response._data.get("uds_path"):
            return real_fd(uds)
        return -1
