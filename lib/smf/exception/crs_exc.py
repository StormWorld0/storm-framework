from .base_exc import BaseException


class CRSRuntimeError(BaseException):
    pass


class CRSException(BaseException):
    pass


class CRSProtocolError(BaseException):
    pass


class CRSStderrError(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class CRSBrokenError(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)
