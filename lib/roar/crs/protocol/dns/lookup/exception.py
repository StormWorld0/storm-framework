class StackTrace(Exception):
    """Melempar Exception stack trace dari response CRS"""

    def __init__(self, status: str = None, message: str = None):
        super().__init__()
        self.status = status
        self.message = message


class TimeoutTrace(Exception):
    """Melempar Exception timeout dari response CRS"""

    def __init__(self, status: str = None, message: str = None):
        super().__init__()
        self.status = status
        self.message = message


class NXDomain(Exception):
    """Melempar Exception NXDOMAIN dari response CRS"""

    def __init__(self, status: str = None, message: str = None):
        super().__init__()
        self.status = status
        self.message = message
