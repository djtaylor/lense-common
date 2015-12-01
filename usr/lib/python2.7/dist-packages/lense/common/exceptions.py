class AuthUserError(Exception):
    """
    User account does not exists or is inactive.
    """
    def __init__(self, user):
        super(AuthUserInactive, self).__init__('User account "{0}" does not exists or is inactive'.format(user))

class AuthError(Exception):
    pass

class RequestError(Exception):
    """
    Custom exception for handling request errors.
    """
    def __init__(self, msg, code):
        super(RequestError, self).__init__(msg)
        self.code = code

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