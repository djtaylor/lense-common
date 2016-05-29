from django.db.models import BooleanField, CharField

class Permissions(object):
    """
    Database model for storing object permissions.
    """
    object_uuid  = CharField(max_length=64, unique=True)
    owner        = CharField(max_length=64, unique=True)
    group        = CharField(max_length=64, unique=True)
    share        = BooleanField(default=False)
    user_read    = BooleanField(default=False)
    user_write   = BooleanField(default=False)
    user_exec    = BooleanField(default=False)
    group_read   = BooleanField(default=False)
    group_write  = BooleanField(default=False)
    group_exec   = BooleanField(default=False)
    all_read     = BooleanField(default=False)
    all_write    = BooleanField(default=False)
    all_exec     = BooleanField(default=False)
    
    # Custom model metadata
    class Meta:
        db_table = 'permissions'