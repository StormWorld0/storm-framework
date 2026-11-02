from .base_exc import BaseException


class CRSRuntimeError(BaseException):
    def __init__(self, sts: str = None, msg: str = None):
        self.message = msg
        super().__init__(f"status: {sts} | message: {msg}")


class CRSException(BaseException):
    def __init__(self, sts: str = None, msg: str = None):
        self.message = msg
        super().__init__(f"status: {sts} | message: {msg}")


class CRSProtocolError(BaseException):
    def __init__(self, sts: str = None, msg: str = None):
        self.message = msg
        super().__init__(f"status: {sts} | message: {msg}")


class CRSKeybordInterrupt(KeyboardInterrupt):
    def __init__(self, sts: str = None, msg: str = None):
        self.message = msg
        super().__init__(f"status: {sts} | message: {msg}")


class CRSBrokenError(BaseException):
    def __init__(self, sts: str = None, msg: str = None):
        self.message = msg
        super().__init__(f"status: {sts} | message: {msg}")


class CRSConnectionRefused(BaseException):
    def __init__(self, sts: str = None, msg: str = None):
        self.message = msg
        super().__init__(f"status: {sts} | message: {msg}")
