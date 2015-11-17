# Django Libraries
from django.db.models import Manager

# Lense Libraries
from lense.common.objects.group.queryset import APIGroupsQuerySet

class APIGroupsManager(Manager):
    """
    Custom objects manager for the APIGroups model. Acts as a link between the main APIGroups
    model and the custom APIGroupsQuerySet model.
    """
    def __init__(self, *args, **kwargs):
        super(APIGroupsManager, self).__init__()
    
    def get_queryset(self, *args, **kwargs):
        """
        Wrapper method for the internal get_queryset() method.
        """
        return APIGroupsQuerySet(model=self.model)