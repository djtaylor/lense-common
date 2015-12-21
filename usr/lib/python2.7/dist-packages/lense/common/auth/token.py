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
            
        # Create a new API token
        LENSE.LOG.info('Generating API token for user: {0}'.format(user))
        return LENSE.OBJECTS.USER.grant_token(user)
    
    @staticmethod
    def update(user):
        """
        Update a users API token.
        
        :param user: The user account to update the token for
        :type  user: str
        """
        
        # Update the user's token
        LENSE.LOG.info('Updating API token for user: {0}'.format(user))
        return LENSE.OBJECTS.USER.grant_token(user, overwrite=True)
    
    @staticmethod
    def get(user):
        """
        Get the API authentication token for a user or host account.
        
        :param user: The user account to retrieve the token for
        :type  user: str
        """
         
        # Get the user API token
        api_token = LENSE.ensure(LENSE.OBJECTS.USER.get_token(user),
            isnot = None,
            error = 'Could not retrieve API token user {0}'.format(user),
            debug = 'Retrieved user {0} API token'.format(user),
            code  = 404)

        # User has no API token
        if not user.api_token:
            LENSE.LOG.error('API user "{0}" has no token in the database'.format(user))
            return None
        
        # Return the API token
        return api_token
    
    @staticmethod
    def validate(user, usr_token):
        """
        Validate the API token for a user or host account.
        
        :param       user: The user account to validate
        :type        user: str
        :param  usr_token: The user submitted API token to validate
        :type   usr_token: str
        :rtype: bool
        """
        
        # Get the user object
        user = LENSE.ensure(LENSE.OBJECTS.USER.get(user),
            error = 'Could not find user {0}'.format(user),
            debug = 'Found user {0} object'.format(user),
            code  = 404)
        
        # Get the API token
        db_token = LENSE.ensure(AuthAPIToken.get(user),
            error = 'Could not retrieve API token for user {0}'.format(user),
            debug = 'Retrieved API token for user {0}'.format(user),
            code  = 404)
        
        # Invalid token in request
        if not db_token == usr_token:
            raise AuthError('User "{0}" has submitted an invalid API token'.format(user))
        return True