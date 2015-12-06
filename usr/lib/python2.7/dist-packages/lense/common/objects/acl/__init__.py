from lense import import_class
from lense.common.objects.base import LenseBaseObject

class ACL_Keys(LenseBaseObject):
    """
    Wrapper classed used to retrieve ACL key definitions.
    """
    def __init__(self):
        super(ACL_Keys, self).__init__('lense.common.objects.acl.models', 'ACLKeys')

class ACL_Objects(LenseBaseObject):
    """
    Wrapper classed used to retrieve ACL object definitions.
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