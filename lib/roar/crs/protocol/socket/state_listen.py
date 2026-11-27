import smf


class ListenState:
    """Socket listener state management"""

    def __init__(self, state, cfd: int | None = None):
        self.state = state
        self._cfd = cfd
        self._is_closed_cfd = False
        self._local_client_fd = -1

    def _ensure_open(self, operation: str):
        """Prevent execution in a closed session"""
        if self.state._is_closed or self._is_closed_cfd:
            smf.printd(
                f"Cannot {operation} on a closed Socket client session.", level="ERROR"
            )
            raise RuntimeError(
                f"Cannot execute {operation}() on a closed Socket client session."
            )
