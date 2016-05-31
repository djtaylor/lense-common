from lense.common.objects.base import LenseBaseObject

class ObjectInterface(LenseBaseObject):
    def __init__(self):
        super(ObjectInterface, self).__init__('lense.common.objects.group.models', 'APIGroups')
        
        # Group members
        self.MEMBERS = LenseBaseObject('lense.common.objects.group.models', 'APIGroupMembers')
        
    def extend(self, group):
        """
        Construct extended group attributes.
        
        :param group: The group object to extend
        :type  group: APIGroup
        :rtype: APIUser
        """
        uuid = LENSE.OBJECTS.getattr(group, 'uuid')
        
        # Extend the user object
        for k,v in {
            'members': [x.group.uuid for x in self.MEMBERS.get(group=uuid)],
            'acls': self.get_acls(group=uuid)
        }.iteritems():
            self.log('Extending group {0} attributes -> {1}={2}'.format(uuid,k,v), level='debug', method='extend')
            LENSE.OBJECTS.setattr(group, k, v)
        return group
        
    def get(self, **kwargs):
        """
        Retrieve an object definition.
        """
        group = super(ObjectInterface, self).get(**kwargs)
        
        # No group found
        if not group:
            return None
        
        # Multiple group objects
        if isinstance(group, list):
            for g in group:
                self.extend(g)
            return group
        
        # Single group object
        return self.extend(group)    
    
    def get_permissions(self, group):
        """
        Construct an object of a group's permissions.
        
        :param  group: The group UUID
        :type   group: str
        :rtype: dict|None
        """
        if not self.exists(uuid=group):
            return None
        
        # Global / object level permissions
        return {
            'global': LENSE.OBJECTS.ACL.PERMISSIONS('global').get(owner=group),
            'object': LENSE.OBJECTS.ACL.PERMISSIONS('object').get(owner=group)
        }
        
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
    
    def get_acls(self, group):
        """
        Construct ACLs for a group.
        """
        return {
            'object': LENSE.OBJECTS.dump(LENSE.OBJECTS.ACL.PERMISSIONS('object').get(**{'owner': group})),
            'global': LENSE.OBJECTS.dump(LENSE.OBJECTS.ACL.PERMISSIONS('global').get(**{'owner': group}))
        }