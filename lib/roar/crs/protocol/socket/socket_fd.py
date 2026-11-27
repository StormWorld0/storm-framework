import os
import fcntl
from .state_build import IPCPayloadBuilder
from .response import SocketResponse
from .utils_fd import real_fd
from ...endpoint import CRS


class ListenFD:
    """Special class instance from Accept function"""

    def fileno(self, **kwargs) -> int:
        """
        Retrieving Client Socket FD using `SCM_RIGHTS`
        and save the fd to the local state cache for further use.

        There are now 2 active FD Clients belonging to Python and Golang that refer to the same socket,
        and need `close(fileno)` mechanism to close these 2 Client FDs!
        """
        self._ensure_open("fileno")
        if self._local_client_fd != -1:
            return self._local_client_fd

        packet = IPCPayloadBuilder.build(
            state=self.state,
            cfd=self._cfd,
            mode="fileno-clt",
        )

        resp = CRS.send(packet)
        response = SocketResponse(resp)

        if uds := response._data.get("client_uds"):
            fd = real_fd(uds)
            self._local_client_fd = fd
            return self._local_client_fd
        return -1


class SocketFD:
    """Special class inherited from Socket"""

    def fileno(self, **kwargs) -> int:
        """
        Retrieving the FD of a Python prose table with `SCM_RIGHTS`
        and save the fd locally for future use!

        Now there are 2 active FDs belonging to Python and Golang that refer to the same socket,
        and need `close(fileno)` mechanism to close these 2 active FDs,
        except for the transfer of FD ownership which only requires using the object close() from the new owner!
        """
        self._ensure_open("fileno")
        if self._sock_fd != -1:
            return self._sock_fd

        packet = IPCPayloadBuilder.build(
            state=self,
            mode="fileno",
        )

        resp = SocketResponse(CRS.send(packet))
        if uds := resp._data.get("socket_uds"):
            fd = real_fd(uds)
            self._sock_fd = fd
            return self._sock_fd
        return -1

    def getbloking(self) -> bool:
        """
        View FD status
        True if blocking and False if non-blocking
        """
        self._ensure_open("getbloking")
        packet = IPCPayloadBuilder.build(
            state=self,
            mode="getbloking",
        )
        
        resp = SocketResponse(CRS.send(packet))
        if not resp.ok:
            raise OSError("Failed to check FD status")
            
        is_block = resp._data.get("status-fd")
        return is_block
