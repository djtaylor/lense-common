from uuid import UUID

# Lense Libraries
from lense import import_class

class LenseGroup(object):
    """
    Commons class for retrieving groups and group members.
    """
    def __init__(self, group=None):
        """
        :param group: Set the internal group name/UUID
        :type  group: str
        """
        self.model   = import_class('APIGroups', 'lense.common.objects.group.models', init=False)
        self.members = import_class('APIGroupMembers', 'lense.common.objects.group.models', init=False)
        self.id      = group
        
    
    def _filter(self, group):
        """
        Map a group name or UUID to filter parameters.
        """
        try:
            UUID(group, version=4)
            return {'uuid': group}
        except ValueError:
            return {'name': group}
    
    def exists(self, group):
        """
        Check if a group exists by group name or UUID.
        
        :param group: Group name or UUID to check for.
        :type  group: str
        :rtype: bool
        """
        exists_uuid = self.model.objects.filter(uuid=group).count()
        exists_name = self.model.objects.filter(name=group).count()
        
        # Group exists
        if exists_uuid or exists_name:
            return True
        return False
    
    def members(self, group):
        """
        Return a list of member UUIDs for a group.
        """
        if not self.exists(group):
            return None
        
        # Get the group
        group = self.get(group)
        
        # Return any members
        return group.members_list()
    
    def remove_member(self, group, user):
        """
        Remove a user from a group.
        
        :param group: The group to remove the user from
        :type  group: str
        :param  user: The user object to remove from the group
        :type   user: user
        :rtype: bool
        """
        if not self.exists(group) or not LENSE.USER.exists(user):
            return False
    
        # Get the group and user
        group = self.get(group)
        user  = LENSE.USER.get(user)
    
        # Remove the user from the group
        try:
            group.members_unset(user)
            return True
        except Exception as e:
            LENSE.LOG.exception('Failed to remove user "{0}" from group "{1}": {2}'.format(user.username, group.name))
            return False
    
    def add_member(self, group, user):
        """
        Add a user to a group.
        
        :param group: The group to enroll the user in
        :type  group: str
        :param  user: The user object to add to the group
        :type   user: user
        :rtype: bool
        """
        if not self.exists(group) or not LENSE.USER.exists(user):
            return False
        
        # Get the group and user objects
        group = self.get(group)
        user  = LENSE.USER.get(user)
        
        # Add the user to the group
        try:
            group.members_set(user)
            return True
        except Exception as e:
            LENSE.LOG.exception('Failed to add user "{0}" to group "{1}": {2}'.format(user.username, group.name))
            return False
    
    def has_members(self, group, user=None):
        """
        Check if a group has any members.
        
        :param group: Group name or UUID
        :type  group: str
        :rtype: bool
        """
        if not self.exists(group):
            return False
        
        # Get the group object
        group = self.get(group)
        
        # Return any group members
        if not user:
            return self.members.filter(group=group.uuid).count()
    
        # Looking for a specific user
        if user in self.members(group):
            return True
        return False
    
    def create(self, **kwargs):
        """
        Attempt to create a new group.
        """
        try:
            self.model(**kwargs).save()
            return True
            
        # Failed to create group
        except Exception as e:
            LENSE.LOG.exception('Failed to create group "{0}": {1}'.format(kwargs.get('name', None), str(e)))
            return False
    
    def delete(self, group):
        """
        Attempt to delete a group.
        
        :param group: The group name or UUID to delete
        :type  group: str
        """
        if not self.exists(group):
            LENSE.LOG.error('Failed to delete group "{0}", not found in database'.format(group))
            return False
        
        # Get the group object
        group = self.get(group)
    
        # Delete the group
        group.delete()
    
    def get(self, group):
        """
        Retrieve a group object by group name or UUID.
        
        :param group: The group name or UUID to retrieve
        :type  group: str
        """
        if self.exists(group):
            return self.model.objects.get(**self._filter(group))
            
        # Group doesn't exist
        LENSE.LOG.error('Group "{0}" not found in database'.format(group))
        return None
    
    def set(self, group):
        """
        Return an instance of the LenseGroup class initialized with a group name/UUID.
        
        :param group: The group name / UUID
        :type  group: str
        :rtype: LenseGroup
        """
        if self.exists(group):
            return LenseGroup(group)