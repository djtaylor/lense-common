from lense import import_class
from lense.common.objects.base import LenseBaseObject

class ObjectInterface(object):
    """
    Interface classed used to load the various ACL object handlers.
    """
    def __init__(self):
        self.KEYS    = LenseBaseObject('lense.common.objects.acl.models', 'ACLKeys')
        self.OBJECTS = LenseBaseObject('lense.common.objects.acl.models', 'ACLObjects')
        
    def PERMISSIONS(self, access_type):
        """
        Wrapper method for returning ACL permissions object methods.
        
        :param access_type: The access type to retrieve (global or object)
        :type  access_type: str
        :rtype: object
        """
        return {
            'global': LenseBaseObject('lense.common.objects.acl.models', 'ACLPermissions_Global'),
            'object': LenseBaseObject('lense.common.objects.acl.models', 'ACLPermissions_Object')
        }.get(access_type, None)
        
    def ACCESS(self, access_type):
        """
        Wrapper method for returning ACL access type object methods.
        
        :param access_type: The access type to retrieve (global or object)
        :type  access_type: str
        :rtype: object
        """
        return {
            'global': LenseBaseObject('lense.common.objects.acl.models', 'ACLAccess_Global'),
            'object': LenseBaseObject('lense.common.objects.acl.models', 'ACLAccess_Object')
        }.get(access_type, None)