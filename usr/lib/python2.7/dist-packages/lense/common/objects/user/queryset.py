# Django Libraries
from django.db.models.query import QuerySet

# Lense Libraries
from lense.common.vars import G_ADMIN

class APIUserQuerySet(QuerySet):
    """
    Custom query set for the user model.
    """
    
    # Timestamp format / timefield keys
    timestamp  = '%Y-%m-%d %H:%M:%S'
    timefields = ['date_joined', 'last_login']
    
    def __init__(self, *args, **kwargs):
        super(APIUserQuerySet, self).__init__(*args, **kwargs)

        # Resolve circular imports
        from lense.common.objects.group.models import APIGroups, APIGroupMembers

        # API groups / group members
        self.APIGroups = APIGroups
        self.APIGroupMembers = APIGroupMembers

    def _is_admin(self, user):
        """
        Check if the user is a member of the administrator group.
        """
        groups = self._get_groups(user)
        for group in groups:
            if group['uuid'] == G_ADMIN:
                return True
        return False

    def _get_groups(self, user):
        """
        Retrieve a list of group membership.
        """
        membership = []
        for g in self.APIGroupMembers.objects.filter(member=user).values():
            gd = self.APIGroups.objects.filter(uuid=g['group_id']).values()[0]
            membership.append({
                'uuid': gd['uuid'],
                'name': gd['name'],
                'desc': gd['desc']
            })
        return membership

    def values(self, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Store the initial results
        _u = super(APIUserQuerySet, self).values(*fields)
        
        # Process each user object definition
        for user in _u:
            
            # Parse any time fields
            for timefield in self.timefields:
                if timefield in user:
                    user[timefield] = user[timefield].strftime(self.timestamp)
            
            # Remove the password
            del user['password']
            
            # Get user groups and administrator status
            user.update({
                'groups': self._get_groups(user['uuid']),
                'is_admin': self._is_admin(user['uuid'])
            })
        
        # Return the constructed user results
        return _u

