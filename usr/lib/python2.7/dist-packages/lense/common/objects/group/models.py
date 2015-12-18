import re
import json
import importlib
from uuid import uuid4

# Django Libraries
from django.db.models import Model, ForeignKey, CharField, NullBooleanField

# Lense Libraries
from lense import import_class
from lense.common.objects.acl.models import ACLObjects
from lense.common.objects.group.manager import APIGroupsManager
from lense.common.objects.acl.models import ACLGroupPermissions_Global, ACLKeys

class APIGroupMembers(Model):
    """
    Database model that stores group membership.
    """
    group     = ForeignKey('group.APIGroups', to_field='uuid', db_column='group')
    member    = ForeignKey('user.APIUser', to_field='uuid', db_column='member')
    
    # Custom model metadata
    class Meta:
        db_table = 'api_group_members'

class APIGroups(Model):
    """
    Database model that contains API group information.
    """
    uuid      = CharField(max_length=36, unique=True, default=str(uuid4()))
    name      = CharField(max_length=64, unique=True)
    desc      = CharField(max_length=128)
    protected = NullBooleanField()
    
    # Custom objects manager
    objects   = APIGroupsManager()
    
    def object_permissions_set(self, permissions):
        """
        Set object permissions for this group.
        """
    
        # Get a list of object types and details
        obj_types   = []
        obj_details = []
        for obj in ACLObjects.objects.all().values():
            obj_types.append(obj['type'])
            obj_details.append(obj)
        
        # Process each object type in the request
        for obj_type in obj_types:
            if obj_type in permissions:
                
                # Get the details for this ACL object type
                obj_def   = ACLObjects.objects.get(**{'type': obj_type}).values()[0]
                
                # Get an instance of the ACL class
                acl_mod   = importlib.import_module(obj_def['acl_mod'])
                acl_class = getattr(acl_mod, obj_def['acl_cls'])
                acl_key   = obj_def['acl_key']
                
                # Process each object
                for obj_id, obj_acls in permissions[obj_type].iteritems():
                
                    # Get an instance of the object class
                    obj_mod   = importlib.import_module(obj_def['obj_mod'])
                    obj_class = getattr(obj_mod, obj_def['obj_cls'])
                    obj_key   = obj_def['obj_key']
                
                    # Object filter
                    obj_filter = {}
                    obj_filter[obj_key] = obj_id
                
                    # Process each ACL definition
                    for acl_id, acl_val in obj_acls.iteritems():
                
                        # Define the filter dictionairy
                        filter = {}
                        filter['owner'] = self.uuid
                        filter['acl']   = acl_id
                        filter[acl_key] = obj_id
                    
                        # Revoke the permission
                        if acl_val == 'remove':
                            acl_class.objects.filter(**filter).delete()
                            
                        # Modify the permission
                        else:
                            
                            # If creating a new ACL entry
                            if not acl_class.objects.filter(**filter).count():
                                
                                # Model fields
                                fields = {}
                                fields['acl']     = ACLKeys.objects.get(uuid=acl_id)
                                fields['owner']   = self
                                fields[obj_type]  = obj_class.objects.get(**obj_filter)
                                fields['allowed'] = acl_val
                                
                                # Create a new ACL entry
                                acl_class(**fields).save()
                                
                            # If updating an existing ACL entry
                            else:
                                obj = acl_class.objects.get(**filter)
                                obj.allowed = acl_val
                                obj.save()
                
    
    def global_permissions_set(self, permissions):
        """
        Set global permissions for this group.
        """
        
        # Get any existing global permissions
        gp_current = [x['acl_id'] for x in list(ACLGroupPermissions_Global.objects.filter(owner=self.uuid).values())]
        
        # Process each permission definition
        for key,value in permissions.iteritems():
            
            # If ACL already exists
            if key in gp_current:
                
                # If removing the ACL completely
                if value == 'remove':
                    ACLGroupPermissions_Global.objects.filter(owner=self.uuid, acl=key).delete()
                
                # If updating the ACL
                else:
                    acl = ACLGroupPermissions_Global.objects.get(owner=self.uuid, acl=key)
                    acl.allowed = value
                    acl.save()
                
            # If adding a new ACL
            else:
                acl = ACLGroupPermissions_Global(
                    acl     = ACLKeys.objects.get(uuid=key),
                    owner   = self,
                    allowed = value
                )
                acl.save()
    
    def members_list(self):
        """
        Retrieve a compact list of group member names.
        """
        return [m['member_id'] for m in APIGroupMembers.objects.filter(group=self.uuid).values()]
    
    def members_get(self):
        """
        Retrieve a list of group member objects.
        """
        api_user = import_class('APIUser', 'lense.common.objects.user.models', init=False)
        
        # Return a list of user member objects
        return [api_user.objects.get(uuid=m.member) for m in APIGroupMembers.objects.filter(group=self.uuid)]
        
    def members_set(self, m):
        """
        Add a member to the group.
        """
        APIGroupMembers(group=self, member=m).save()
    
    def members_unset(self, m):
        """
        Remove a member from the group.
        """
        APIGroupMembers.objects.filter(group=self.uuid).filter(member=m.uuid).delete()
    
    # Custom model metadata
    class Meta:
        db_table = 'api_groups'