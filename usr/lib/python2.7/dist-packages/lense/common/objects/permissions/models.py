from django.db.models import Model, BooleanField, CharField

class Permissions(Model):
    """
    Database model for storing object permissions.
    """
    object_uuid  = CharField(max_length=64)
    owner        = CharField(max_length=64)
    group        = CharField(max_length=64)
    share        = BooleanField(default=False)
    user_read    = BooleanField(default=False)
    user_write   = BooleanField(default=False)
    user_delete  = BooleanField(default=False)
    user_exec    = BooleanField(default=False)
    group_read   = BooleanField(default=False)
    group_write  = BooleanField(default=False)
    group_delete = BooleanField(default=False)
    group_exec   = BooleanField(default=False)
    all_read     = BooleanField(default=False)
    all_write    = BooleanField(default=False)
    all_delete   = BooleanField(default=False)
    all_exec     = BooleanField(default=False)
    
    def __repr__(self):
        return '<{0}({1})>'.format(self.__class__.__name__, self.object_uuid)
    
    # Custom model metadata
    class Meta:
        db_table = 'permissions'