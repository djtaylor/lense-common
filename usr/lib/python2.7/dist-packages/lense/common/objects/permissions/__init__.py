from lense.common.vars import USERS, GROUPS
from lense.common.objects.base import LenseBaseObject

class ObjectInterface(LenseBaseObject):
    def __init__(self):
        super(ObjectInterface, self).__init__('lense.common.objects.permissions.models', 'Permissions')
        
    def flush(self, obj):
        """
        Flush all permissions for an existing object.
        """
        object_uuid   = LENSE.OBJECTS.getattr(obj, 'uuid')
        
        # Object has no UUID attributes
        if not object_uuid:
            self.log('Object has no UUID, skipping permissions...', level='debug', method='flush')
            return
        
        # Delete permissinos
        self.model.objects.filter(object_uuid=object_uuid).delete()
        self.log('Flushing permissions for <{0}>'.format(object_uuid), level='debug', method='flush')
        
    def create(self, obj, permissions={}):
        """
        Create permissions for a new object.
        """
        object_uuid   = LENSE.OBJECTS.getattr(obj, 'uuid')
        
        # Object has no UUID attributes
        if not object_uuid:
            self.log('Object has no UUID, skipping permissions...', level='debug', method='create')
            return
        
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
            'user_delete': True,
            'user_exec': True,
            'group_read': True,
            'group_write': True,
            'group_delete': True,
            'group_exec': True
        }
        
        # Custom permissions
        for k,v in permissions.iteritems():
            params[k] = v
        
        # Set permissions
        self.log('Setting permissions on object "{0}": owner={1}, group={2}'.format(object_uuid, owner, group), level='debug', method='create')
        permissions = self.model(**params)
        permissions.save()
        