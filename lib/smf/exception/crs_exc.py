from .base_exc import BaseException


class CRSRuntimeError(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class CRSException(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class CRSProtocolError(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class CRSKeybordInterrupt(KeyboardInterrupt):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class CRSBrokenError(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)
