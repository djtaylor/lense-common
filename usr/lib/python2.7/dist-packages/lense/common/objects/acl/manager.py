
# Django Libraries
from django.db.models import Manager

# Lense Libraries
from lense.common.objects.acl.queryset import ACLObjectsQuerySet, ACLKeysQuerySet

class ACLKeysManager(Manager):
    """
    Custom objects manager for the ACLKeys model.
    """
    def __init__(self, *args, **kwargs):
        super(ACLKeysManager, self).__init__()
    
    def get_queryset(self, *args, **kwargs):
        """
        Wrapper method for the internal get_queryset() method.
        """
        return ACLKeysQuerySet(model=self.model)

class ACLObjectsManager(Manager):
    """
    Custom objects manager for the ACLObjects model.
    """
    def __init__(self, *args, **kwargs):
        super(ACLObjectsManager, self).__init__()
    
    def get_queryset(self, *args, **kwargs):
        """
        Wrapper method for the internal get_queryset() method.
        """
        return ACLObjectsQuerySet(model=self.model)