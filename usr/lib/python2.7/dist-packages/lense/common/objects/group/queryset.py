# Django Libraries
from django.db.models.query import QuerySet

# Lense Libraries
from lense.common.objects.acl import ACLObjects
from lense.common.objects.user.models import APIUser
from lense.common.objects.acl.models import ACLKeys, ACLGroupPermissions_Global

class APIGroupsQuerySet(QuerySet):
    """
    Custom queryset manager for the DBGroupDetails model. This allows customization of the returned
    QuerySet when extracting host details from the database.
    """
    def __init__(self, *args, **kwargs):
        super(APIGroupsQuerySet, self).__init__(*args, **kwargs)
        
        # Group members import
        from lense.common.objects.group.models import APIGroupMembers
        
        # Group members model
        self.APIGroupMembers = APIGroupMembers
        
    def _object_permissions_get(self, group):
        """
        Construct a list of object permissions for hosts for this group.
        """
        
        # Process object permission flags
        def _process_flags(flags):
            ret_flags = {}
            for k,v in flags.iteritems():
                if not k in ret_flags:
                    ret_flags[k] = v
            return ret_flags
        
        # Construct the object permissions
        ret = {}
        for obj_details in ACLObjects.get_values():
            obj_type  = obj_details['type']
            obj_key   = '{0}_id'.format(obj_type)
            
            # Get an instance of the ACL class
            acl_def   = ACLObjects.get_values(obj_type)[0]
            acl_mod   = importlib.import_module(acl_def['acl_mod'])
            acl_class = getattr(acl_mod, acl_def['acl_cls'])
            
            # Get the object details
            try:
                acl_obj   = list(acl_class.objects.filter(owner=group['uuid']).values())
            except Exception as e:
                print 'YEP - FAILED: {0}'.format(str(e))
            
            for acl in acl_obj:
                acl['object_id'] = acl[obj_key]
                del acl[obj_key]
            
            # Create the object permissions for this type
            ret[obj_type] = {
                'ids':     {},
                'details': acl_obj
            }
            
            # Set the object IDs
            for acl in acl_obj:
                obj_id = acl['object_id']
                if not obj_id in ret[obj_type]['ids']:
                    ret[obj_type]['ids'][obj_id] = []
                ret[obj_type]['ids'][obj_id].append(acl['acl_id'])
        
        # Return the constructed object permissions
        return ret
        
    def _global_permissions_get(self, group):
        """
        Construct a list of global permissions for this group.
        """
        global_permissions = []
        
        # Process each global permission definition for the group
        for global_permission in ACLGroupPermissions_Global.objects.filter(owner=group['uuid']).values():
            
            # Get the ACL details for this permission definition
            acl_details = ACLKeys.objects.filter(uuid=global_permission['acl_id']).values()[0]
        
            # Update the return object
            global_permissions.append({
                'acl':      acl_details['name'],
                'uuid':     acl_details['uuid'],
                'desc':     acl_details['desc'],
                'allowed':  'yes' if global_permission['allowed'] else 'no'      
            })
            
        # Return the constructed permissions object
        return global_permissions
        
    def _extract_permissions(self, group):
        """
        Extract group permissions.
        """
        return {
            'global': self._global_permissions_get(group),
            'object': self._object_permissions_get(group)
        }
        
    def _extract_members(self, group):
        """
        Extract group members.
        """
        
        # Resolve circular dependencies
        from lense.engine.api.app.user.models import DBUser
        
        # Extract group membership
        members = []
        for member in list(self.APIGroupMembers.objects.filter(group=group['uuid']).values()):
            
            # Get the member user object
            user_obj = APIUser.objects.get(uuid=member['member_id'])
            members.append({
                'uuid':       user_obj.uuid,
                'username':   user_obj.username,
                'email':      user_obj.email,
                'is_enabled': user_obj.is_active,
                'fullname':   user_obj.get_full_name()
            })
            
        # Return the membership list
        return members
        
    def _extract(self, group):
        """
        Extract details for an API user group.
        """
        
        # Group membership / permissions
        group['members']     = self._extract_members(group)
        group['permissions'] = self._extract_permissions(group)
        
        # Return the constructed group object
        return group
        
    def values(self, detailed=False, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Store the initial results
        _r = super(APIGroupsQuerySet, self).values(*fields)
        
        # Group return object
        _a = []
        
        # Process each group object definition
        for group in _r:
            _a.append(self._extract(group))
        
        # Return the constructed group results
        return _a