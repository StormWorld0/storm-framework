class TelnetResponse:
    """Mengelola Response Telnet"""
    
    @property
    def ok(self) -> bool:
        """Returns True on success"""
        return self.resp_con.ok

    @property
    def status(self) -> str:
        """Status string of the open process (SUCCESS/ERROR/TIMEOUT)."""
        return self.resp_con.status

    @property
    def message(self) -> str:
        """Detailed message of the open connection process."""
        return self.resp_con.message
