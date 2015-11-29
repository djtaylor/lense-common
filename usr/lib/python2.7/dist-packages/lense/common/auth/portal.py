from lense import import_class
from lense.common.exceptions import AuthError

class AuthPortal(object):
    """
    Portal authentication handler.
    """
    @staticmethod
    def validate(user, password):
        auth = import_class('authenticate', 'django.contrib.auth', init=False)
 
        # User does not exists or is inactive
        LENSE.USER.ensure('exists', exc=AuthError, msg='User "{0}" does not exist'.format(user), args=[user])       
        LENSE.USER.ensure('active', exc=AuthError, msg='User "{0}" is inactive'.format(user), args=[user])
 
        # Try user/password authentication
        if not auth(username=user, password=password):
            raise AuthError('Invalid username/password')

        # Authorization OK
        return True