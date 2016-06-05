from datetime import datetime, timedelta

# Django Libraries
from django.conf import settings

# Lense Libraries
from lense.common.utils import rstring
from lense.common.auth import AuthBase
from lense.common.exceptions import AuthError

class AuthAPIToken(AuthBase):
    """
    API class used to assist in validating, creating, and retrieving API authentication tokens.
    """
    def create(self, user):
        """
        Generate a new API authentication token.
        
        :param user: The user account to generate the token for
        :type  user: str
        """
            
        # Create a new API token
        return self.ensure(LENSE.OBJECTS.USER.grant_token(user),
            isnot = None,
            error = 'Failed to generate API token for user: {0}'.format(user),
            debug = 'Generating API token for user: {0}'.format(user),
            code  = 500)
    
    def update(self, user):
        """
        Update a users API token.
        
        :param user: The user account to update the token for
        :type  user: str
        """
        
        # Update the user's token
        return self.ensure(LENSE.OBJECTS.USER.grant_token(user, overwrite=True),
            isnot = None,
            error = 'Failed to update API token for user: {0}'.format(user),
            debug = 'Updating API token for user: {0}'.format(user),
            code  = 500)
    
    def get(self, user):
        """
        Get the API authentication token for a user or host account.
        
        :param user: The user account to retrieve the token for
        :type  user: str
        """
         
        # Get the user API token
        api_token = self.ensure(LENSE.OBJECTS.USER.get_token(user),
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
    
    def validate(self, user, usr_token):
        """
        Validate the API token for a user or host account.
        
        :param       user: The user account to validate
        :type        user: str
        :param  usr_token: The user submitted API token to validate
        :type   usr_token: str
        :rtype: bool
        """
        
        # Get the user object
        user = self.ensure(LENSE.OBJECTS.USER.get_internal(**LENSE.OBJECTS.USER.map_uuid(user)),
            error = 'Could not find user {0}'.format(user),
            debug = 'Found user {0} object'.format(user),
            code  = 404)
        
        # Get the API token
        db_token = self.ensure(self.get(user),
            error = 'Could not retrieve API token for user {0}'.format(user),
            debug = 'Retrieved API token for user {0}'.format(user),
            code  = 404)
        
        # Validate the token
        return self.ensure((db_token == usr_token),
            error = 'User "{0}" has submitted an invalid API token'.format(user),
            debug = 'User "{0}" has submitted a valid API token'.format(user),
            code  = 401)