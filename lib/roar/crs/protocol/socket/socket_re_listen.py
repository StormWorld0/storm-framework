from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from ...endpoint import CRS
from typing import Tuple


class ListenResolv:
    """Special class to handle Resolver Listener"""

    def getsockname(self) -> Tuple[str, int]:
        """Get local socket IP"""
        self._ensure_open("getsockname")
        packet = IPCPayloadBuilder.build(
            state=self.state,
            cfd=self._cfd,
            mode="getsockname",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        return response.local_ip

    def getpeername(self) -> Tuple[str, int]:
        """Get socket server IP"""
        self._ensure_open("getpeername")
        packet = IPCPayloadBuilder.build(
            state=self.state,
            cfd=self._cfd,
            mode="getpeername",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        return response.remote_ip
