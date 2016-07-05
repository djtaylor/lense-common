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
            'members': [x.group.uuid for x in LENSE.OBJECTS.as_list(self.MEMBERS.get(group=uuid))]
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
        
        # Make sure user is not already a member
        LENSE.ensure(self.has_member(group, member),
            value = False,
            code  = 400,
            error = 'User {0} is already a member of group {1}'.format(member, group))
        
        # Get the group and user objects
        group = self.get_internal(uuid=group)
        user  = LENSE.OBJECTS.USER.get(uuid=member)
        
        # Add the user to the group
        try:
            group.members_set(user)
            return True
        except Exception as e:
            LENSE.LOG.exception('Failed to add user "{0}" to group "{1}": {2}'.format(user.username, group.name, str(e)))
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
    
        # Make sure user is a member
        LENSE.ensure(self.has_member(group, member),
            value = True,
            code  = 400,
            error = 'User {0} is not a member of group {1}'.format(member, group))
    
        # Get the group and user
        group = self.get_internal(uuid=group)
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
        group = self.get_internal(uuid=group)
        
        # Return any members
        return group.members_list()
    
    def create(self, **kwargs):
        """
        Create a new user group.
        """
        
        # Unique attributes
        for key in ['name', 'uuid']:
            LENSE.ensure(self.exists(**{key: kwargs[key]}),
                value = False,
                code  = 400,
                error = 'Cannot create group, duplicate entry for key {0}'.format(key))
            
        # Create the group
        group = LENSE.ensure(super(ObjectInterface, self).create(**kwargs),
            isnot = False,
            error = 'Failed to create group: {0}'.format(kwargs['uuid']),
            log   = 'Created group: {0}'.format(kwargs['uuid']),
            code  = 500)
        
        # Return the new group object
        return self.get(uuid=group.uuid)
    
    def delete(self, **kwargs):
        """
        Delete an existing user group.
        """

        # Get the group
        group = LENSE.ensure(self.get(uuid=kwargs['uuid']),
            error = 'Could not locate group object {0}'.format(kwargs['uuid']),
            debug = 'Group object {0} exists, retrieved object'.format(kwargs['uuid']),
            code  = 404)

        # Make sure the group isn't protected
        LENSE.ensure(group.protected, 
            value = False,
            error = 'Cannot deleted protected group {0}'.format(group.uuid),
            code  = 400)

        # Make sure the group has no members
        LENSE.ensure(self.get_members(group.uuid),
            value = [],
            error = 'Cannot delete group {0}, still has members'.format(group.uuid),
            code  = 400)

        # Delete the group
        LENSE.ensure(super(ObjectInterface, self).delete(uuid=group.uuid),
            error = 'Failed to delete group {0}'.format(group.uuid),
            log   = 'Deleted group {0}'.format(group.uuid),      
            code  = 500)
    
    def update(self, **kwargs):
        """
        Update a group object.
        """
        uuid = LENSE.extract(kwargs, 'uuid')
        
        # Get the group
        group = LENSE.ensure(super(ObjectInterface, self).get(uuid=uuid),
            isnot = None,
            error = 'Could not find group',
            code  = 404)
        
        # Update the group
        super(ObjectInterface, self).update(group, **kwargs)
        
        # Get and return the updated group
        return self.get(uuid=uuid)