import importlib

# Django Libraries
from django.db.models import Model, ForeignKey, CharField, SET_NULL, \
                             TextField, NullBooleanField, BooleanField

# Lense Libraries
from lense.common.objects.acl.manager import ACLObjectsManager, ACLKeysManager

class ACLObjects(Model):
    """
    Main database model for storing ACL object types.
    """
    uuid        = CharField(max_length=36, unique=True)
    name        = CharField(max_length=36)
    object_type = CharField(max_length=36, unique=True)
    object_mod  = CharField(max_length=128)
    object_cls  = CharField(max_length=64)
    object_key  = CharField(max_length=36)
    def_acl     = ForeignKey('acl.ACLKeys', to_field='uuid', db_column='def_acl', null=True, blank=True, on_delete=SET_NULL)

    # Unique ID field
    UID_FIELD = 'uuid'

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
    
    # Unique ID field
    UID_FIELD = 'uuid'
    
    # Custom objects manager
    objects     = ACLKeysManager()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_keys'
        
class ACLAccess_Object(Model):
    """
    Main database model for storing global ACL access keys.
    """
    acl        = ForeignKey('acl.ACLKeys', to_field='uuid', db_column='acl')
    handler    = ForeignKey('handler.Handlers', to_field='uuid', db_column='request_handler')
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_access_global'

class ACLAccess_Global(Model):
    """
    Main database model for storing object level ACL access keys.
    """
    acl        = ForeignKey('acl.ACLKeys', to_field='uuid', db_column='acl')
    handler    = ForeignKey('handler.Handlers', to_field='uuid', db_column='request_handler')
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_access_object'
        
class ACLPermissions_Object(Model):
    """
    Main database model for storing object level access to user groups.
    """
    acl         = ForeignKey('acl.ACLKeys', to_field='uuid', db_column='acl')
    object_id   = CharField(max_length=128)
    object_type = CharField(max_length=32)
    owner       = ForeignKey('group.APIGroups', to_field='uuid', db_column='owner')
    allowed     = NullBooleanField()
        
    # Custom table metadata
    class Meta:
        db_table = 'acl_object_permissions'
        
class ACLPermissions_Global(Model):
    """
    Main database model for storing global level access to user groups.
    """
    acl        = ForeignKey('acl.ACLKeys', to_field='uuid', db_column='acl')
    owner      = ForeignKey('group.APIGroups', to_field='uuid', db_column='owner')
    allowed    = NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_global_permssions'
