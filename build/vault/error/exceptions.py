
class VaultError(Exception):
    '''Base application exception'''
    def __init__(self, statusCode, message=None):
        if (message is None):
            message = "An unspecified application error occured."
        super(Exception, self).__init__(message)
        self.statusCode = statusCode


class CmdError(VaultError):
    pass


class NetworkError(VaultError):
    pass

class SecurityError(VaultError):
    pass
