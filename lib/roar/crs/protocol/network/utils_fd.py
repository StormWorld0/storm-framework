import socket
import struct
import fcntl


def real_fd(uds_path: str) -> int:
    """Retrieve original FD via UDS"""
    if not uds_path.startswith("@"):
        return -1

    # The CPython API recognizes the null byte (\x00) at the beginning of an address as an Abstract Namespace marker
    addr = uds_path.replace("@", "\x00", 1)

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(addr)

            # Calculate buffer size for integer
            fd_size = struct.calcsize("@i")

            # recvmsg returns: payload data, ancillary data (CMSG), flags, address
            # socket.CMSG_SPACE allocates proper padding according to POSIX standard
            _, ancdata, _, _ = sock.recvmsg(1, socket.CMSG_SPACE(fd_size))

            local_fd = -1

            # Parsing control messages (Ancillary Data)
            for cmsg_level, cmsg_type, cmsg_data in ancdata:
                # Verify that the payload is a transfer of access rights (SCM_RIGHTS)
                if cmsg_level == socket.SOL_SOCKET and cmsg_type == socket.SCM_RIGHTS:
                    local_fd = struct.unpack("@i", cmsg_data[:fd_size])[0]
                    break

            if local_fd < 0:
                return -1

            # Implementation of FD Isolation (O_CLOEXEC)
            # Architectural Note: Starting with Python 3.4 (PEP 446), all newly created FDs
            # is non-inheritable by default. However, explicit implementation
            # still recommended as defense-in-depth to prevent FD from leaking to child processes (e.g. during os.exec).
            flags = fcntl.fcntl(local_fd, fcntl.F_GETFD)
            fcntl.fcntl(local_fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)

            return local_fd
    except (OSError, struct.error):
        return -1
