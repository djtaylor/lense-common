class AuthUserError(Exception):
    """
    User account does not exists or is inactive.
    """
    def __init__(self, user):
        super(AuthUserInactive, self).__init__('User account "{0}" does not exists or is inactive'.format(user))
        
class EnsureError(Exception):
    """
    Custom exception for handling ensure errors.
    """
    def __init__(self, msg, code=500):
        super(EnsureError, self).__init__(msg)
        self.code = code

class AuthError(EnsureError):
    pass

class RequestError(EnsureError):
    pass

class ClientError(Exception):
    pass

class JSONException(Exception):
    """
    Custom exceptions when encountering JSON object errors.
    """
    pass

class InvalidProjectID(Exception):
    """
    Wrapper class for handling invalid project names.
    """
    def __init__(self, project):
        super(InvalidProjectID, self).__init__('Invalid project ID: {0}'.format(project))