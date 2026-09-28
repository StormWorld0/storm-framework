# -- https://github.com/StormWorld0/storm-framework
# -- License SMF
# -- Author zxelzy

import smf


from .state_build import SocketState, IPCPayloadBuilder
from .response import SocketResponse, SockTrace
from .constants import ConstantsMix

from ...transport import CRS


class Socket(SocketState, ConstantsMix):
    """
    Facade Antarmuka Eksternal.
    Mewarisi SocketState untuk mempertahankan kompatibilitas atribut (Backward Compatibility).
    Hanya berfokus pada eksekusi instruksi jaringan ke Engine Go.
    """

    STrace = SockTrace

    def socket(
        self,
        addrf: str | int,
        stype: str | int,
        sproto: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Open Socket"""
        self._ensure_open("socket")
        packet = IPCPayloadBuilder.build(
            state=self,
            addr_fam=addrf,
            stype=stype,
            sproto=sproto,
            mode="socket",
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def setsockopt(
        self,
        level: str | int,
        name: str | int,
        value: int = None,
        **kwargs,
    ) -> SocketResponse:
        """Socket Options Configuration"""
        self._ensure_open("setsockopt")
        packet = IPCPayloadBuilder.build(
            state=self,
            level=level,
            name=name,
            value=value,
            mode="setsockopt",
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def bind(
        self,
        host: str,
        port: str | int,
        **kwargs,
    ) -> SocketResponse:
        """Binding local connection"""
        self._ensure_open("bind")
        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            mode="bind",
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def listen(
        self,
        readsize: int,
        **kwargs,
    ) -> SocketResponse:
        """Waiting for incoming connection"""
        self._ensure_open("listen")
        packet = IPCPayloadBuilder.build(
            state=self,
            readsize=readsize,
            mode="listen",
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def accept(
        self,
        **kwargs,
    ) -> SocketResponse:
        """Retrieving Incoming Connections"""
        self._ensure_open("accept")
        packet = IPCPayloadBuilder.build(
            state=self,
            mode="accept",
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def connect(
        self,
        host: str,
        port: str | int = None,
        **kwargs,
    ) -> SocketResponse:
        """Open Connection"""
        self._ensure_open("connect")
        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            mode="connect",
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def send(
        self,
        data: str | bytes,
        timeout: float = None,
        **kwargs,
    ) -> SocketResponse:
        """Sending data"""
        self._ensure_open("send")
        packet = IPCPayloadBuilder.build(
            state=self,
            data=data,
            timeout=timeout,
            infotls=False,
            mode="send",
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def recv(
        self,
        readsize: int = None,
        timeout: float = None,
        **kwargs,
    ) -> SocketResponse:
        """Taking Buffer"""
        self._ensure_open("recv")
        packet = IPCPayloadBuilder.build(
            state=self,
            readsize=readsize,
            timeout=timeout,
            infotls=False,
            mode="recv",
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def sendto(
        self,
        data: str | bytes,
        host: str,
        port: str | int = None,
        flag: str | int = None,
        timeout: float = None,
        **kwargs,
    ) -> SocketResponse:
        """Send datagram along with Host & Port"""
        self._ensure_open("sendto")
        packet = IPCPayloadBuilder.build(
            state=self,
            data=data,
            host=host,
            port=port,
            flag=flag,
            timeout=timeout,
            infotls=False,
            mode="sendto",
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def recvfrom(
        self,
        readsize: int = None,
        flag: str | int = None,
        timeout: float = None,
        **kwargs,
    ) -> SocketResponse:
        """Taking Buffer"""
        self._ensure_open("recvfrom")
        packet = IPCPayloadBuilder.build(
            state=self,
            readsize=readsize,
            flag=flag,
            timeout=timeout,
            infotls=False,
            mode="recvfrom",
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

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

    def create_connection(
        self,
        host: str,
        port: str | int = None,
        timeout: float = None,
        **kwargs,
    ) -> SocketResponse:
        """Creating a TCP Stream connection"""
        self._ensure_open("create")
        packet = IPCPayloadBuilder.build(
            state=self,
            host=host,
            port=port,
            timeout=timeout,
            mode="create",
            infotls=False,
            close_session=False,
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)
        response._trace()
        return response

    def close(self) -> SocketResponse:
        """Disconnecting"""
        if self._is_closed:
            return SocketResponse(
                {"status": "already_closed", "session_id": self.sessid, "data": {}}
            )

        packet = IPCPayloadBuilder.build(state=self, mode="close", close_session=True)
        resp = CRS.send(packet)
        self._is_closed = True

        response = SocketResponse(resp)
        response._trace()
        return response

    def timeout(self, value: float):
        """Global Timeout"""
        self._timeout = value
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self):
        tls_state = "TLS" if self.is_tls else "TCP"
        return f"<Socket host='{self.host}:{self.port}' proto='{tls_state}' sessid='{self.sessid}' closed={self._is_closed}>"
