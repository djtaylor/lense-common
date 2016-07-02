from uuid import uuid4

# Django Libraries
from django.db.models import Model, CharField, TextField, NullBooleanField, BooleanField, ForeignKey

# Lense Libraries
from lense.common.objects.models import JSONField

class Handlers(Model):
    """
    Main database model for storing API request handler details.
    """
    uuid         = CharField(max_length=36, unique=True, default=str(uuid4()))
    name         = CharField(max_length=128, unique=True)
    path         = CharField(max_length=128)
    desc         = CharField(max_length=256)
    method       = CharField(max_length=6)
    mod          = CharField(max_length=128)
    cls          = CharField(max_length=64, unique=True)
    protected    = NullBooleanField()
    enabled      = BooleanField()
    allow_anon   = NullBooleanField()
    locked       = NullBooleanField()
    locked_by    = CharField(max_length=64, null=True, blank=True)
    backend      = CharField(max_length=16, default='python')
    
    def __repr__(self):
        return '<{0}({1})>'.format(self.__class__.__name__, self.uuid)
    
    # Custom table metadata
    class Meta:
        db_table = 'request_handlers'
        
class HandlerManifests(Model):
    """
    Main database model for storing handler manifests if being used.
    """
    handler    = ForeignKey('handler.Handlers', to_field='uuid', db_column='handler')
    json       = JSONField(empty=True)
    
    def __repr__(self):
        return '<{0}({1})>'.format(self.__class__.__name__, self.uuid)
    
    # Custom table metadata
    class Meta:
        db_table = 'request_handler_manifests'