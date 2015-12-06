from lense import import_class
from lense.common.objects.base import LenseBaseObject

class ACL_Keys(LenseBaseObject):
    """
    Wrapper class used to retrieve ACL key definitions.
    """
    def __init__(self):
        super(ACL_Keys, self).__init__('lense.common.objects.acl.models', 'ACLKeys')

class ACL_Objects(LenseBaseObject):
    """
    Wrapper class used to retrieve ACL object definitions.
    """
    def __init__(self):
        super(ACL_Objects, self).__init__('lense.common.objects.acl.models', 'ACLObjects')
        
class ACL_Objects_Interface(object):
    """
    Interface classed used to load the various ACL object handlers.
    """
    def __init__(self):
        self.KEYS    = ACL_Keys()
        self.OBJECTS = ACL_Objects()
        
    def PERMISSIONS(self, access_type, object_type=None):
        """
        Wrapper method for returning ACL permissions object methods.
        
        :param access_type: The access type to retrieve (global or object)
        :type  access_type: str
        :param access_type: The object type to retrieve
        :type  access_type: str
        :rtype: object
        """
        access_map = {
            'global': LenseBaseObject('lense.common.objects.acl.models', 'ACLGroupPermissions_Global'),
            'object': {
                'group':   ['lense.common.objects.acl.models', 'ACLGroupPermissions_Object_Group'],
                'user':    ['lense.common.objects.acl.models', 'ACLGroupPermissions_Object_User'],
                'handler': ['lense.common.objects.acl.models', 'ACLGroupPermissions_Object_Handler']    
            }
        }
        
        # Global permissions
        if access_type == 'global':
            return LenseBaseObject(access_map.get('global')[0], access_map.get('global')[1])
        
        # Object permissions
        if object_type:
            object_map = access_map.get('object').get(object_type, None)
            if not object_map:
                return None
            return LenseBaseObject(object_map[0], object_map[1])
        
    def ACCESS(self, access_type):
        """
        Wrapper method for returning ACL access type object methods.
        
        :param access_type: The access type to retrieve (global or object)
        :type  access_type: str
        :rtype: object
        """
        return {
            'global': LenseBaseObject('lense.common.objects.acl.models', 'ACLGlobalAccess'),
            'object': LenseBaseObject('lense.common.objects.acl.models', 'ACLObjectAccess')
        }.get(access_type, None)