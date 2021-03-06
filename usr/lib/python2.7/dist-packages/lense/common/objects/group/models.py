import re
import json
import importlib
from uuid import uuid4

# Django Libraries
from django.db.models import Model, ForeignKey, CharField, NullBooleanField

# Lense Libraries
from lense import import_class

class APIGroupMembers(Model):
    """
    Database model that stores group membership.
    """
    uuid      = CharField(max_length=36, unique=True, default=str(uuid4()))
    group     = ForeignKey('group.APIGroups', to_field='uuid', db_column='group')
    member    = ForeignKey('user.APIUser', to_field='uuid', db_column='member')
    
    def __repr__(self):
        return '<{0}({1})>'.format(self.__class__.__name__, self.uuid)
    
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
    
    # Extended fields
    EX_FIELDS = ['members']
    
    def __repr__(self):
        return '<{0}({1})>'.format(self.__class__.__name__, self.uuid)
    
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
        APIGroupMembers(group=self, member=m, uuid=LENSE.uuid4()).save()
    
    def members_unset(self, m):
        """
        Remove a member from the group.
        """
        APIGroupMembers.objects.filter(group=self.uuid).filter(member=m.uuid).delete()
    
    # Custom model metadata
    class Meta:
        db_table  = 'api_groups'