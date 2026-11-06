from .base_exc import StormBaseException


class CRSRuntimeError(StormBaseException):
    def __init__(self, sts: str = None, msg: str = None):
        self.message = msg
        super().__init__(f"status: {sts} | message: {msg}")


class CRSException(StormBaseException):
    def __init__(self, sts: str = None, msg: str = None):
        self.message = msg
        super().__init__(f"status: {sts} | message: {msg}")


class CRSProtocolError(StormBaseException):
    def __init__(self, sts: str = None, msg: str = None):
        self.message = msg
        super().__init__(f"status: {sts} | message: {msg}")


class CRSKeybordInterrupt(KeyboardInterrupt):
    def __init__(self, sts: str = None, msg: str = None):
        self.message = msg
        super().__init__(f"status: {sts} | message: {msg}")


class CRSBrokenError(StormBaseException):
    def __init__(self, sts: str = None, msg: str = None):
        self.message = msg
        super().__init__(f"status: {sts} | message: {msg}")


class CRSConnectionRefused(StormBaseException):
    def __init__(self, sts: str = None, msg: str = None):
        self.message = msg
        super().__init__(f"status: {sts} | message: {msg}")
