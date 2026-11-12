from .base_exc import StormBaseException


class HttpError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class HttpTimeout(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class HttpValueError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)
