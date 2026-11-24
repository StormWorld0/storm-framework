from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .socket_tls_obj import ObjectTLS
from ...endpoint import CRS


class SocketTLS:
    """List all TLS upgrade sockets"""

    def uptls(
        self,
        cert: str,
        key: str,
        ca: str | None = None,
        verify: bool = True,
        **kwargs,
    ) -> tuple[object, object]:
        """
        Upgrade connection to TLS/SSL

        `uptls` returns 2 elements `conn, resp = uptls()`
        `conn` refers to a derived object `uptls`
        which can be used to perform I/O operations and set options
        or take options up to close() or close(fileno)
        """
        self._ensure_open("uptls")
        if self.is_tls:
            return SocketResponse({"status": "WARN", "message": "Already TLS"})

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
        return ObjectTLS(state=self), SocketResponse(resp)
