from .base_exc import BaseException

class SocketError(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)


class SocketConnectionRefused(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)


class SocketTimeout(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)
