import importlib

# Django Libraries
from django.db.models import Model, ForeignKey, CharField, \
                             TextField, NullBooleanField, BooleanField

# Lense Libraries
from lense.common.objects.acl.manager import ACLObjectsManager, ACLKeysManager

class ACLGlobalAccess(Model):
    """
    Main database model for storing global ACL access keys.
    """
    acl        = ForeignKey('acl.ACLKeys', to_field='uuid', db_column='acl')
    utility    = ForeignKey('utility.Utilities', to_field='uuid', db_column='utility')
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_access_global'

class ACLObjectAccess(Model):
    """
    Main database model for storing object level ACL access keys.
    """
    acl        = ForeignKey('acl.ACLKeys', to_field='uuid', db_column='acl')
    utility    = ForeignKey('utility.Utilities', to_field='uuid', db_column='utility')
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_access_object'

class ACLObjects(Model):
    """
    Main database model for storing ACL object types.
    """
    uuid       = CharField(max_length=36, unique=True)
    type       = CharField(max_length=36, unique=True)
    name       = CharField(max_length=36)
    acl_mod    = CharField(max_length=128)
    acl_cls    = CharField(max_length=64, unique=True)
    acl_key    = CharField(max_length=36)
    obj_mod    = CharField(max_length=128)
    obj_cls    = CharField(max_length=64)
    obj_key    = CharField(max_length=36)
    def_acl    = ForeignKey('acl.ACLKeys', to_field='uuid', db_column='def_acl', null=True, blank=True, on_delete=SET_NULL)

    # Custom objects manager
    objects    = ACLObjectsManager()

    # Custom table metadata
    class Meta:
        db_table = 'acl_objects'

class ACLKeys(Model):
    """ 
    Main database model for storing ACL keys and details. Each ACL can handle
    authorization for any number of utilities.
    """
    uuid        = CharField(max_length=36, unique=True)
    name        = CharField(max_length=128, unique=True)
    desc        = CharField(max_length=128)
    type_object = BooleanField()
    type_global = BooleanField()
    
    # Custom objects manager
    objects     = ACLKeysManager()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_keys'
    
class ACLGroupPermissions_Object_Group(Model):
    """
    Main database model for storing object ACL permissions for group objects.
    """
    acl        = ForeignKey(DBGatewayACLKeys, to_field='uuid', db_column='acl')
    group      = ForeignKey('group.APIGroups', to_field='uuid', db_column='group', related_name='group_target')
    owner      = ForeignKey('group.APIGroups', to_field='uuid', db_column='owner', related_name='group_owner')
    allowed    = NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_permissions_object_group'

class ACLGroupPermissions_Object_User(Model):
    """
    Main database model for storing object ACL permissions for group objects.
    """
    acl        = ForeignKey(DBGatewayACLKeys, to_field='uuid', db_column='acl')
    user       = ForeignKey('user.DBUser', to_field='uuid', db_column='user')
    owner      = ForeignKey('group.APIGroups', to_field='uuid', db_column='owner')
    allowed    = NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_permissions_object_user'
        
class ACLGroupPermissions_Object_Utility(Model):
    """
    Main database model for storing object ACL permissions for utility objects.
    """
    acl        = ForeignKey(DBGatewayACLKeys, to_field='uuid', db_column='acl')
    utility    = ForeignKey(DBGatewayUtilities, to_field='uuid', db_column='utility')
    owner      = ForeignKey('group.APIGroups', to_field='uuid', db_column='owner')
    allowed    = NullBooleanField()
        
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_permissions_object_utility'
        
class ACLGroupPermissions_Global(Model):
    """
    Main database model for storing global ACL permissions for groups.
    """
    acl        = ForeignKey('acl.ACLKeys', to_field='uuid', db_column='acl')
    owner      = ForeignKey('group.APIGroups', to_field='uuid', db_column='owner')
    allowed    = NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_permissions_global'
