from lense import import_class
from lense.common.auth import AuthBase
from lense.common.exceptions import AuthError

class AuthPortal(object):
    """
    Portal authentication handler.
    """
    @staticmethod
    def validate(user, password):
        auth = import_class('authenticate', 'django.contrib.auth', init=False)
 
        # Get the user object
        user_object = LENSE.AUTH.ensure(LENSE.OBJECTS.USER.get(username=user),
            isnot = None,
            error = 'Could authenticate user "{0}": not found'.format(user),
            debug = 'User "{0}" discovered, proceeded with authentication'.format(user),
            code  = 404)
 
        # Make sure is active
        LENSE.AUTH.ensure(user_object.is_active,
            value = True,
            error = 'Authentication failed, user "{0}" is inactive'.format(user),
            debug = 'User "{0}" is active, proceeding with authentication'.format(user),
            code  = 401)
 
        # Attempt to authenticate the user
        auth_user = auth(username=user, password=password)
 
        # Authentication failed
        if not auth_user:
            raise AuthError('Invalid username/password')

        # Authorization OK
        return auth_user