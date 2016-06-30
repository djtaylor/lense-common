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

class ClientError(EnsureError):
    pass

class ManifestError(EnsureError):
    def __init__(self, msg):
        super(ManifestError, self).__init__(msg, code=400)

class SecurityError(EnsureError):
    pass

class PermissionsError(Exception):
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
        
class InitializeError(Exception):
    """
    Wrapper class for handling project intialization errors.
    """
    def __init__(self, project, reason='An unknown error occurred'):
        super(InitializeError, self).__init__('Failed to initialize project {0}: {1}'.format(project, reason))