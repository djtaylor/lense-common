from lense.common.vars import USERS, GROUPS
from lense.common.objects.base import LenseBaseObject

class ObjectInterface(LenseBaseObject):
    def __init__(self):
        super(ObjectInterface, self).__init__('lense.common.objects.permissions.models', 'Permissions')
        
    def create(self, obj):
        """
        Create permissions for a new object.
        """
        object_uuid   = LENSE.OBJECTS.getattr(obj, 'uuid')
        
        # Request user/group
        request_user  = LENSE.REQUEST.USER.name
        request_group = LENSE.REQUEST.USER.group
        
        # Owner / group
        owner         = USERS.ADMIN.UUID if not request_user else LENSE.OBJECTS.USER.get_uuid(request_user)
        group         = USERS.ADMIN.GROUP if (request_group == 'anonymous' or not request_group) else request_group
        
        # Parameters
        params        = {
            'object_uuid': object_uuid,
            'owner': owner,
            'group': group,
            'user_read': True,
            'user_write': True,
            'user_exec': True,
            'group_read': True,
            'group_write': True,
            'group_exec': True
        }
        
        # Set permissions
        self.log('Setting permissions on object "{0}": owner={1}, group={2}'.format(object_uuid, owner, group))
        permissions = self.model(**params)
        permissions.save()
        