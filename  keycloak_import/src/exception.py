"""Customize Exception"""


class StoresError(Exception):
    """Exception for generic store errors"""

    def __init__(self, message: object):
        self.message = message
        super().__init__(self.message)


class ResourceNotFoundError(StoresError):
    """Exception for item not found"""

    def __init__(self, message: object):
        self.message = message
        super().__init__(self.message)


class ResourceAlreadyExistsError(StoresError):
    """Exception for item already exists"""

    def __init__(self, message: object):
        self.message = message
        super().__init__(self.message)


class DecodingScriptNotFoundError(StoresError):
    """Exception for item already exists"""

    def __init__(self, message: object):
        self.message = message
        super().__init__(self.message)


class MultiableBacknetGatewayError(Exception):
    """Exception for more then one backnet gateway"""

    def __init__(self, message: object):
        self.message = message
        super().__init__(self.message)
