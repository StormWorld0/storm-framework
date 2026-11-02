from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from ...endpoint import CRS


class SocketTLS:
    """Daftar semua socket upgrade TLS"""

    def uptls(
        self,
        cert: str,
        key: str,
        ca: str = None,
        verify: bool = True,
        **kwargs,
    ) -> SocketResponse:
        """Upgrade connection to TLS/SSL"""
        self._ensure_open("uptls")
        if self.is_tls:
            return SocketResponse(
                {"status": "WARN", "message": "Already TLS", "data": {}}
            )

        packet = IPCPayloadBuilder.build(
            state=self,
            cert=cert,
            key=key,
            ca=ca,
            verify=verify,
            infotls=True,
            mode="upgrade-tls",
        )

        resp = CRS.send(packet)
        if resp.get("status") == "SUCCESS":
            self.is_tls = True
        return SocketResponse(resp)
