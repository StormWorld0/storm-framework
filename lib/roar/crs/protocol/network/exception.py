class SockTrace(Exception):
    """Melempar socket trace dari response CRS Engine"""

    def __init__(self, status: str, message: str):
        self.status = status
        self.message = message
        super().__init__(message)
