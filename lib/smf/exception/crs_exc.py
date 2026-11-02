from .base_exc import BaseException


class CRSRuntimeError(BaseException):
    pass


class CRSException(BaseException):
    pass


class CRSStderrError(BaseException):
    pass


class CRSProtocolError(BaseException):
    pass
