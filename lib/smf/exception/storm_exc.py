from .base_exc import StormBaseException


class SMFRuntimeError(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)


class SMFException(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)


class SMFTypeError(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)


class SMFFileNotFoundError(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)


class SMFOSError(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)


class SMFImportError(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)


class SMFBinaryError(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)


class SMFBrokenPipeError(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)


class SMFConfigDatabaseError(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)


class SMFDatabaseError(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)


class SMFMemoryError(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)


class SMFConnectionError(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)


class SMFSyncError(StormBaseException):
    def __init__(self, *args):
        self.message = *args
        super().__init__(*args)
