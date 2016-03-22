from lense import import_class
from lense.common.objects.base import LenseBaseObject

class ACLObjectsInterface(LenseBaseObject):
    def __init__(self):
        super(ACLObjectsInterface, self).__init__('lense.common.objects.acl.models', 'ACLObjects')

    def get_children(self, acl_object):
        """
        Get any child objects for an ACL object type.
        """
        try:
            return import_class(acl_object['object_cls'], acl_object['object_mod'], init=False).objects.all().count()
            
        # Could not get children
        except Exception as e:
            self.log('Failed to retrieve children: {0}'.format(str(e)), level='exception', method='get_children')
            return 0 

    def extend(self, acl_object):
        """
        Construct extended ACL object attributes.
        
        :param user: The user object to extend
        :type  user: APIUser
        :rtype: APIUser
        """
        uuid = LENSE.OBJECTS.getattr(acl_object, 'uuid')
        
        # Extend the user object
        for k,v in {
            'children': self.get_children(acl_object)
        }.iteritems():
            self.log('Extending ACL object {0} attributes -> {1}={2}'.format(uuid,k,v), level='debug', method='extend')
            LENSE.OBJECTS.setattr(acl_object, k, v)
        return acl_object
        
    def get(self, **kwargs):
        """
        Retrieve an object definition.
        """
        acl_object = super(ACLObjectsInterface, self).get(**kwargs)
        
        # No ACL object found
        if not acl_object:
            return None
        
        # Multiple ACL objects
        if isinstance(acl_object, list):
            for a in acl_object:
                self.extend(a)
            return acl_object
        
        # Single ACL object
        return self.extend(acl_object)

class ObjectInterface(object):
    """
    Interface classed used to load the various ACL object handlers.
    """
    def __init__(self):
        self.KEYS    = LenseBaseObject('lense.common.objects.acl.models', 'ACLKeys')
        self.OBJECTS = ACLObjectsInterface()
        
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