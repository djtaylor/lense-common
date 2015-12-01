from datetime import datetime, timedelta

# Django Libraries
from django.conf import settings

# Lense Libraries
from lense.common.utils import rstring
from lense.common.exceptions import AuthError

class AuthAPIToken(object):
    """
    API class used to assist in validating, creating, and retrieving API authentication tokens.
    """
    @staticmethod
    def create(user):
        """
        Generate a new API authentication token.
        
        :param user: The user account to generate the token for
        :type  user: str
        """
        token_str = rstring(255)
        expires   = datetime.now() + timedelta(hours=settings.API_TOKEN_LIFE)
            
        # Create a new API token
        LENSE.LOG.info('Generating API token for user: {0}'.format(user))
        LENSE.USER.set_token(user, token, expires)
        
        # Return the token
        return token_str
    
    @staticmethod
    def get(user):
        """
        Get the API authentication token for a user or host account.
        
        :param user: The user account to retrieve the token for
        :type  user: str
        """
        
        # Check if the user exists
        if not LENSE.USER.exists(user):
            LENSE.LOG.error('API user "{0}" does not exist in database'.format(user))
            return None

        # Get the user object / and API token
        api_user  = LENSE.USER.get(user)
        api_token = LENSE.USER.token(user)

        # User has no API key
        if not api_token:
            LENSE.LOG.error('API user "{0}" has no token in the database'.format(user))
            return None
        
        # Return the API token
        return api_token
    
    @staticmethod
    def validate(user, token):
        """
        Validate the API token in a request from either a user or host account.
        
        :param  user: The user account to validate
        :type   user: str
        :param token: The incoming API token to validate
        :type  token: str
        :rtype: bool
        """
        
        # User does not exists or is inactive
        LENSE.USER.ensure('exists', exc=AuthError, msg='User "{0}" does not exist'.format(user), args=[user])       
        LENSE.USER.ensure('active', exc=AuthError, msg='User "{0}" is inactive'.format(user), args=[user])
        
        # Get the users API token
        auth = LENSE.USER.token(user)
        
        # User has no token
        if not auth:
            raise AuthError('User "{0}" has no API token'.format(user))
        
        # Invalid API token
        if not auth == token:
            raise AuthError('User "{0}" has submitted an invalid API token'.format(user))
        return True