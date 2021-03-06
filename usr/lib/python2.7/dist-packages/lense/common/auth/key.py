from lense.common.auth import AuthBase
from lense.common.exceptions import AuthError
from lense.common.utils import rstring

class AuthAPIKey(AuthBase):
    """
    API class used to handle validating, retrieving, and generating API keys.
    """
    def create(self, user):
        """
        Generate a new API authentication key.
        
        :param user: The user account to generate the key for
        :type  user: str
        """
            
        # Create a new API key
        return self.ensure(LENSE.OBJECTS.USER.grant_key(user),
            isnot = None,
            error = 'Failed to generate API key for user: {0}'.format(user),
            debug = 'Generating API key for user: {0}'.format(user),
            code  = 500)
    
    def update(self, user):
        """
        Update a users API key.
        
        :param user: The user account to update the key for
        :type  user: str
        """
        
        # Update the user's token
        return self.ensure(LENSE.OBJECTS.USER.grant_key(user, overwrite=True),
            isnot = None,
            error = 'Failed to update API key for user: {0}'.format(user),
            debug = 'Updating API key for user: {0}'.format(user),
            code  = 500)
    
    def get(self, user):
        """
        Get the API key of a user or host account.
        
        :param user: The user account to retrieve the key for
        :type  user: str
        """
        
        # Get the user API key
        api_key = self.ensure(LENSE.OBJECTS.USER.get_key(user),
            isnot = None,
            error = 'Could not retrieve API key user {0}'.format(user),
            debug = 'Retrieved user {0} API key'.format(user),
            code  = 404)

        # User has no API key
        if not user.api_key:
            self.log.error('API user "{0}" has no key in the database'.format(user))
            return None
        
        # Return the API key
        return api_key
    
    def validate(self, user, usr_key):
        """
        Validate the API key for a user or host account.
        
        :param     user: The user account to validate
        :type      user: str
        :param  usr_key: The user submitted API key to validate
        :type   usr_key: str
        :rtype: bool
        """
        
        # Get the user object
        user = self.ensure(LENSE.OBJECTS.USER.get_internal(**LENSE.OBJECTS.USER.map_uuid(user)),
            error = 'Could not find user {0}'.format(user),
            debug = 'Found user {0} object'.format(user),
            code  = 404)
        
        # Get the API key
        db_key = self.ensure(self.get(user),
            error = 'Could not retrieve API key for user {0}'.format(user),
            debug = 'Retrieved API key for user {0}'.format(user),
            code  = 404)
        
        # Validate the key
        return self.ensure((db_key == usr_key),
            error = 'User "{0}" has submitted an invalid API key'.format(user),
            debug = 'User "{0}" has submitted a valid API key'.format(user),
            code  = 401)