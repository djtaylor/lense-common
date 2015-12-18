from lense.common.utils import rstring
from lense.common.objects.base import LenseBaseObject

class ObjectInterface(LenseBaseObject):
    def __init__(self):
        super(ObjectInterface, self).__init__('lense.common.objects.user.models', 'APIUser')
        
        # User key and token handlers
        self.KEY = LenseBaseObject('APIUserKeys', 'lense.common.objects.user.models')
        self.TOKEN = LenseBaseObject('APIUserTokens', 'lense.common.objects.user.models')
        
    def grant_key(self, uuid, api_key=rstring(64), overwrite=False):
        """
        Grant an API key to a user account.
        
        :param      uuid: The UUID of the user to grant the key
        :type       uuid: str
        :
        :param overwrite: Overwrite the existing key if one exists.
        :type  overwrite: bool
        :rtype: bool
        """
        user = self.get(uuid=uuid)
        
        # If the user already has a key
        if self.KEY.exists(user=user.username):
            if not overwrite:
                return False
            
            # Update the key
            self.KEY.update(user=user.uuid, api_key=api_key)
        
        # Grant a new key
        else:
            self.KEY.create(user=user.uuid, api_key=api_key)
        return api_key