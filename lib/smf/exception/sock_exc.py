from .base_exc import StormBaseException


class SocketError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SocketConnectionRefused(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SocketTimeout(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SocketValueError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)
