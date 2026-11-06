from .base_exc import StormBaseException


class SMFRuntimeError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFException(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFTypeError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFFileNotFoundError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFOSError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFImportError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFBinaryError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFBrokenPipeError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFConfigDatabaseError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFDatabaseError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFMemoryError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFConnectionError(StormBaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)
