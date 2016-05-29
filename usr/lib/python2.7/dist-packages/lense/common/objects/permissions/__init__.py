from lense.common.vars import PERMISSIONS
from lense.common.collection import merge_dict
from lense.common.objects.base import LenseBaseObject

class ObjectInterface(LenseBaseObject):
    def __init__(self):
        super(ObjectInterface, self).__init__('lense.common.objects.permissions.models', 'Permissions')
        
    def create(self, obj):
        """
        Create permissions for a new object.
        """
        permissions = self.model(**merge_dict({
            'object_uuid': LENSE.OBJECTS.getattr(obj, 'uuid'),
            'owner': LENSE.OBJECTS.USER.get_uuid(LENSE.REQUEST.USER.name),
            'group': LENSE.REQUEST.USER.group
        }, PERMISSIONS))
        permissions.save()
        