from .base_exc import BaseException


class SMFRuntimeError(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFException(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFTypeError(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFFileNotFountError(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFOSError(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFImportError(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFBinaryError(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)


class SMFBrokenPipeError(BaseException):
    def __init__(self, msg: str = None):
        self.message = msg
        super().__init__(msg)
