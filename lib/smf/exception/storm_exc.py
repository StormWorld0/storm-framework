from .base_exc import BaseException


class SMFRuntimeError(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)

class SMFException(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)

class SMFTypeError(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)

class SMFFileNotFoundError(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)

class SMFOSError(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)

class SMFImportError(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)

class SMFBinaryError(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)

class SMFBrokenPipeError(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)

class SMFConfigDatabaseError(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)

class SMFDatabaseError(BaseException):
    def __init__(self, msg: str = None, *args):
        self.message = msg
        super().__init__(msg, args)
