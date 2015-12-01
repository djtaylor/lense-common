from lense.common.exceptions import AuthError
from lense.common.utils import valid, invalid, rstring

class AuthAPIKey(object):
    """
    API class used to handle validating, retrieving, and generating API keys.
    """
    @staticmethod
    def get(user):
        """
        Get the API key of a user or host account.
        
        :param user: The user account to retrieve the key for
        :type  user: str
        """
        
        # User does not exist
        if not LENSE.USER.exists(user):
            LENSE.LOG.error('API user "{0}" does not exist in database'.format(user))
            return None
        
        # Get the user model and API key
        api_user = LENSE.USER.get(user)
        api_key  = LENSE.USER.key(user)

        # User has no API key
        if not api_key:
            LENSE.LOG.error('API user "{0}" has no key in the database'.format(user))
            return None
        
        # Return the API key
        return api_key
    
    @staticmethod
    def validate(user, key):
        """
        Validate the API key for a user or host account.
        
        :param user: The user account to validate
        :type  user: str
        :param  key: The incoming API key to validate
        :type   key: str
        :rtype: bool
        """
        
        # User does not exists or is inactive
        LENSE.USER.ensure('exists', exc=AuthError, msg='User "{0}" does not exist'.format(user), args=[user])       
        LENSE.USER.ensure('active', exc=AuthError, msg='User "{0}" is inactive'.format(user), args=[user])
        
        # Get the API key of the user
        auth = LENSE.USER.key(user)
        
        # User has no key
        if not auth:
            raise AuthError('User "{0}" has no API key'.format(user))
        
        # Invalid key in request
        if not auth == key:
            raise AuthError('User "{0}" has submitted an invalid API key'.format(user))
        return True
    
    @staticmethod
    def create():
        """
        Generate a 64 character API key.
        """
        return rstring(64)