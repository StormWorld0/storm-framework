from .state_build import IPCPayloadBuilder
from .response import SocketResponse

from ...transport import CRS


class SocketTLS:
    """Daftar semua socket upgrade TLS"""

    def uptls(
        self,
        cert: str,
        key: str,
        ca: str = None,
        verify: bool = False,
        **kwargs,
    ) -> SocketResponse:
        """Upgrade connection to TLS/SSL"""
        self._ensure_open("uptls")
        if self.is_tls:
            smf.printd("The connection is already using TLS", level="WARN")
            return SocketResponse(
                {"status": "WARN", "message": "Already TLS", "data": {}}
            )

        packet = IPCPayloadBuilder.build(
            state=self,
            cert=cert,
            key=key,
            ca=ca,
            verify=verify,
            mode="upgrade_tls",
            infotls=True,
            close_session=False,
        )

        resp = CRS.send(packet)
        if resp.get("status") == "SUCCESS":
            self.is_tls = True

        response = SocketResponse(resp)
        response._trace()
        return response
        
