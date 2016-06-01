from lense import import_class
from lense.common.vars import GROUPS

# Access types
FLAGS = ['read', 'write', 'delete', 'exec']

class LensePermissions(object):
    """
    Class for handling permission checks.
    """
    @classmethod
    def log(cls, msg, level='info', method=None):
        logger = getattr(LENSE.LOG, level, 'info')
        logger('<{0}{1}:{2}@{3}> {4}'.format(
            'PERMISSIONS', 
            '' if not method else '.{0}'.format(method), 
            LENSE.REQUEST.USER.name,
            LENSE.REQUEST.client,
            msg
        ))
    
    @classmethod
    def _check_access(cls, obj, access_type):
        """
        Internal method for checking access to an object by access type.
        """
        log_method = '_check_access[{0}]'.format(access_type)
        
        # Permissions model
        MODEL = import_class('Permissions', 'lense.common.objects.permissions.models', init=False)
        
        # Validate access type
        if not access_type in FLAGS:
            cls.log('Invalid access type: {0}'.format(access_type), level='error', method='_check_access')
            return False
        
        # Object UUID
        object_uuid = LENSE.OBJECTS.getattr(obj, 'uuid')
        
        # No UUID
        if not object_uuid:
            cls.log('Object has no UUID: {0}'.format(repr(obj)), level='debug', method=log_method)
            return True
    
        # Disable permissions on bootstrap
        if LENSE.bootstrap:
            cls.log('Project is bootstrapping, permissions disabled', level='debug', method=log_method)
            return True
    
        # Get/set object permissions
        permissions = [LENSE.OBJECTS.dump(x) for x in list(MODEL.objects.filter(object_uuid=object_uuid))]
        setattr(obj, '_permissions', permissions)
        
        # Log permissions
        if object_uuid:
            cls.log('Retrieved permissions: {0}({1}): {2}'.format(
                MODEL.__name__, 
                object_uuid, 
                obj._permissions
            ), level='debug', method='_check_access')
            
        # Confirm access
        api_user   = LENSE.OBJECTS.USER.get_internal(uuid=LENSE.REQUEST.USER.uuid)
        api_group  = LENSE.REQUEST.USER.group    
        access_str = 'User({0}::{1}):{2}:Object({3})'.format(api_user.uuid, api_group, access_type, object_uuid)
        
        # Administrative access
        if GROUPS.ADMIN.UUID in [x['uuid'] for x in api_user.groups]:
            
        
        # Read/write access to self (user)
        if object_uuid == api_user.uuid:
            if access_type in ['read', 'write']:
                cls.log('User access granted to self {0}'.format(access_str), level='debug', method=log_method)
                return True
        
        # Read access to group(s)
        if object_uuid in [x['uuid'] for x in api_user.groups]:
            if access_type in ['read']:
                cls.log('User access granted to own group {0}'.format(access_str), level='debug', method=log_method)
                return True
        
        # Access flags
        access_flag = {
            'user': 'user_{0}'.format(access_type),
            'group': 'group_{0}'.format(access_type),
            'all': 'all_{0}'.format(access_type)
        }
        
        # Check access
        for pr in obj._permissions:
            
            # User level access
            if pr['owner'] == api_user.uuid:
                if pr[access_flag['user']]:
                    cls.log('User access granted {0}'.format(access_str), level='debug', method=log_method)
                    return True
                
            # Group level access
            if pr['group'] == api_group:
                if pr[access_flag['group']]:
                    cls.log('Group access granted {0}'.format(access_str), level='debug', method=log_method)
                    return True
        
            # All level access
            if pr[access_flag['all']]:
                cls.log('All access granted {0}'.format(access_str), level='debug', method=log_method)
                return True
        
        # Access denied
        cls.log('Access denied {0}'.format(access_str), level='debug', method=log_method)
        return False
    
    @classmethod
    def can_read(cls, obj):
        """
        Check if the current API user/group has read access to the object.
        """
        return cls._check_access(obj, 'read')
    
    @classmethod
    def can_write(cls, obj):
        """
        Check if the current API user/group has write access to the object.
        """
        return cls._check_access(obj, 'write')
    
    @classmethod
    def can_delete(cls, obj):
        """
        Check if the current API user/group has delete access to the object.
        """
        return cls._check_access(obj, 'delete')
    
    @classmethod
    def can_exec(cls, obj):
        """
        Check if the current API user/group has execute access to the object.
        """
        return cls._check_access(obj, 'exec')