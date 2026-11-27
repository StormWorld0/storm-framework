import os
import uuid
import socket
import struct
import fcntl
import array
import threading


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


def build_uds(fd: int | None, timeout: float = 3.0) -> str | None:
    if fd is None or fd < 0:
        return None

    # Ensure fd is valid
    os.fstat(fd)

    uds = f"@socket_fd_{uuid.uuid4().hex}"
    real_path = uds.replace("@", "\x00", 1)

    ready = threading.Event()
    startup_error: list[BaseException] = []

    def _serve_once() -> None:
        server: socket.socket | None = None
        conn: socket.socket | None = None
        try:
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server.bind(real_path)
            server.listen(1)
            server.settimeout(timeout)
            ready.set()

            conn, _ = server.accept()
            conn.settimeout(timeout)

            fd_array = array.array("i", [fd])
            ancdata = [(socket.SOL_SOCKET, socket.SCM_RIGHTS, fd_array.tobytes())]
            sent = conn.sendmsg([b"\x01"], ancdata)
            if sent < 1:
                raise RuntimeError("Failed to send payload SCM_RIGHTS")

            # Receive FIN from Go
            fin = conn.recv(1)
            if fin not in (b"", b"\x01"):
                raise ConnectionError("Peer closes connection before sending FIN")
        except BaseException as exc:
            if not ready.is_set():
                startup_error.append(exc)
        finally:
            if conn is not None:
                try:
                    conn.close()
                except OSError:
                    pass
            if server is not None:
                try:
                    server.close()
                except OSError:
                    pass

    worker = threading.Thread(target=_serve_once, daemon=True)
    worker.start()

    if not ready.wait(timeout=timeout):
        raise TimeoutError("UDS listener failed to ready within timeout")

    if startup_error:
        raise startup_error[0]

    return uds
