import json
import string
import random

# CloudScape Libraries
from cloudscape.common.utils import valid, invalid
from cloudscape.engine.api.app.user.models import DBUserAPIKeys, DBUser
from cloudscape.engine.api.app.group.models import DBGroupDetails
from cloudscape.engine.api.app.host.models import DBHostDetails, DBHostAPIKeys

class APIKey(object):
    """
    API class used to handle validating, retrieving, and generating API keys.
    """
    def create(self):
        """
        Generate a 64 character API key.
        """
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(64)])

    def _get_api_key(self, id):
        """
        Retrieve the API key for a user or host account.
        """
        
        # Check if a user or host
        api_user = DBUser.objects.filter(username=id).count()
        api_host = DBHostDetails.objects.filter(uuid=id).count()

        # If not an existing host or user
        if not api_user and not api_host:
            return invalid('Authentication failed, account <> not found in the database' % id)
        
        # If for some reason both a user and host
        if api_user and api_host:
            return invalid('Authentication failed, account <> is both user and host' % id)

        # Get the API key
        if api_user:
            
            # Make sure the user is enabled
            user_obj = DBUser.objects.get(username=id)
            if not user_obj.is_active:
                return invalid('Authentication failed, account <%s> is disabled' % id)
            
            # Return the API key row
            api_key_row = DBUserAPIKeys.objects.filter(user=id).values('api_key')
        if api_host:
            api_key_row = DBHostAPIKeys.objects.filter(host=id).values('api_key')
        db_api_key  = api_key_row[0]['api_key']

        # User or host has no API key
        if not db_api_key: 
            return invalid('Authentication failed, no API key found for account <%s>' % id)
        return valid(db_api_key)

    def validate(self, request):
        """
        Validate the API key for a user or host account.
        """
        
        # Get the API key of the user or host
        api_key = self._get_api_key(id=request['api_user'])
        
        # User has no API key
        if not api_key['valid']: 
            return api_key
            
        # Invalid API key
        if api_key['content'] != request['api_key']:
            return invalid('Client <%s> has submitted an invalid API key' % request['api_user'])
        
        # API key looks OK
        return valid(request)

    def get(self, id):
        """
        Get the API key of a user or host account.
        """
        
        # Get the API key of the user or host
        db_api_key = self._get_api_key(id=id)
        
        # User has no API key
        if not db_api_key: 
            return False
        
        # Return the client API key
        return api_key_row[0]['api_key']