class StackTrace(Exception):
    """Melempar Exception stack trace dari response CRS"""

    def __init__(self, message: str = None):
        self.message = message
        super().__init__(message)


class TimeoutTrace(Exception):
    """Melempar Exception timeout dari response CRS"""

    def __init__(self, message: str = None):
        self.message = message
        super().__init__(message)


class NXDomain(Exception):
    """Melempar Exception NXDOMAIN dari response CRS"""

    def __init__(self, message: str = None):
        super().__init__(message)
