class StackTrace(Exception):
    """Melempar exception Stack Trace dari response CRS"""

    def __init__(self, status: str = None, message: str = None):
        super().__init__(f"Status:'{status}' => Message:'{message}'")


class TimeoutTrace(Exception):
    """Melempar exception Timeout Trace dari response CRS"""

    def __init__(self, status: str = None, message: str = None):
        super().__init__(f"Status:'{status}' => Message:'{message}'")
