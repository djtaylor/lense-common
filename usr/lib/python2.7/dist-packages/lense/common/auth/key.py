from lense.common.exceptions import AuthError
from lense.common.utils import valid, invalid, rstring

class AuthAPIKey(object):
    """
    API class used to handle validating, retrieving, and generating API keys.
    """
    @staticmethod
    def create(user):
        """
        Generate a new API authentication key.
        
        :param user: The user account to generate the key for
        :type  user: str
        """
            
        # Create a new API key
        LENSE.LOG.info('Generating API key for user: {0}'.format(user))
        return LENSE.OBJECTS.USER.grant_key(user)
    
    @staticmethod
    def update(user):
        """
        Update a users API key.
        
        :param user: The user account to update the key for
        :type  user: str
        """
        
        # Update the user's token
        LENSE.LOG.info('Updating API key for user: {0}'.format(user))
        return LENSE.OBJECTS.USER.grant_key(user, overwrite=True)
    
    @staticmethod
    def get(user):
        """
        Get the API key of a user or host account.
        
        :param user: The user account to retrieve the key for
        :type  user: str
        """
        
        # Get the user API key
        api_key = LENSE.ensure(LENSE.OBJECTS.USER.get_key(user),
            isnot = None,
            error = 'Could not retrieve API key user {0}'.format(user),
            debug = 'Retrieved user {0} API key'.format(user),
            code  = 404)

        # User has no API key
        if not user.api_key:
            LENSE.LOG.error('API user "{0}" has no key in the database'.format(user))
            return None
        
        # Return the API key
        return api_key
    
    @staticmethod
    def validate(user, usr_key):
        """
        Validate the API key for a user or host account.
        
        :param     user: The user account to validate
        :type      user: str
        :param  usr_key: The user submitted API key to validate
        :type   usr_key: str
        :rtype: bool
        """
        
        # Get the user object
        user = LENSE.ensure(LENSE.OBJECTS.USER.get(**LENSE.OBJECTS.USER.map_uuid(user)),
            error = 'Could not find user {0}'.format(user),
            debug = 'Found user {0} object'.format(user),
            code  = 404)
        
        # Get the API key
        db_key = LENSE.ensure(AuthAPIKey.get(user),
            error = 'Could not retrieve API key for user {0}'.format(user),
            debug = 'Retrieved API key for user {0}'.format(user),
            code  = 404)
        
        # Invalid key in request
        if not db_key == usr_key:
            raise AuthError('User "{0}" has submitted an invalid API key'.format(user))
        return True