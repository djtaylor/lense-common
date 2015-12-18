from lense.common.objects.base import LenseBaseObject

class ObjectInterface(LenseBaseObject):
    def __init__(self):
        super(ObjectInterface, self).__init__('lense.common.objects.group.models', 'APIGroups')
        
    def add_member(self, group, member):
        """
        Add a member to a group.
        
        :param  group: The group UUID
        :type   group: str
        :param member: The user UUID
        :type  member: str
        """
        
        # Make sure the user/group exists
        if not self.exists(uuid=group) or not LENSE.OBJECTS.USER.exists(uuid=member):
            return False
        
        # Get the group and user objects
        group = self.get(uuid=group)
        user  = LENSE.OBJECTS.USER.get(uuid=member)
        
        # Add the user to the group
        try:
            group.members_set(user)
            return True
        except Exception as e:
            LENSE.LOG.exception('Failed to add user "{0}" to group "{1}": {2}'.format(user.username, group.name))
            return False
    
    def remove_member(self, group, member):
        """
        Remove a member from a group.
        
        :param  group: The group UUID
        :type   group: str
        :param member: The user UUID
        :type  member: str
        """
        
        # Make sure the user/group exists
        if not self.exists(uuid=group) or not LENSE.OBJECTS.USER.exists(uuid=member):
            return False
    
        # Get the group and user
        group = self.get(uuid=group)
        user  = LENSE.OBJECTS.USER.get(uuid=member)
    
        # Remove the user from the group
        try:
            group.members_unset(user)
            return True
        except Exception as e:
            LENSE.LOG.exception('Failed to remove user "{0}" from group "{1}": {2}'.format(user.username, group.name))
            return False
    
    def has_member(self, group, member):
        """
        Check if a group has a particular member.
        
        :param  group: The group UUID
        :type   group: str
        :param member: The user UUID
        :type  member: str
        """
        if not self.exists(uuid=group):
            return False
    
        # Get group members
        members = self.get_members(group)
        
        # Is the user a member
        return True if member in members else False
    
    def get_members(self, group):
        """
        Return a list of member UUIDs for a group.
        
        :param group: The group UUID
        :type  group: str
        """
        if not self.exists(uuid=group):
            return None
        
        # Get the group
        group = self.get(uuid=group)
        
        # Return any members
        return group.members_list()