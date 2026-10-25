from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from ...transport import CRS


class Inspector:
    """Class khusus menangani Inspector Listener"""

    def getsockname(self) -> SocketResponse:
        """Dapatkan IP local socket"""
        self.state._ensure_open("getsockname")
        packet = IPCPayloadBuilder.build(
            state=self,
            cfd=self._cfd,
            mode="getsockname",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response.local_ip

    def getpeername(self) -> SocketResponse:
        """Dapatkan IP server socket"""
        self.state._ensure_open("getpeername")
        packet = IPCPayloadBuilder.build(
            state=self,
            cfd=self._cfd,
            mode="getpeername",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        response._ktrace()
        return response.remote_ip
