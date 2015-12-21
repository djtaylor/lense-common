# Django Libraries
from django.db.models.query import QuerySet

# Lense Libraries
from lense import import_class
from lense.common.vars import GROUPS

class APIUserQuerySet(QuerySet):
    """
    Custom query set for the user model.
    """
    
    # Timestamp format / timefield keys
    timestamp  = '%Y-%m-%d %H:%M:%S'
    timefields = ['date_joined', 'last_login']
    
    # Key values to clean
    clean      = ['password']
    
    def __init__(self, *args, **kwargs):
        super(APIUserQuerySet, self).__init__(*args, **kwargs)

        # API groups / group members
        self.groups = import_class('APIGroups', 'lense.common.objects.group.models', init=False)
        self.group_members = import_class('APIGroupMembers', 'lense.common.objects.group.models', init=False)

    def is_admin(self, user):
        """
        Check if the user is a member of the administrator group.
        """
        groups = self.get_groups(user)
        for group in groups:
            if group['uuid'] == GROUPS.ADMIN.UUID:
                return True
        return False

    def get_groups(self, user):
        """
        Retrieve a list of group membership.
        """
        membership = []
        for g in self.group_members.objects.filter(member=user).values():
            gd = self.groups.objects.filter(uuid=g['group_id']).values()[0]
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
        users = super(APIUserQuerySet, self).values(*fields)
        
        # Process each user object definition
        for user in users:
            
            # Parse any time fields
            for timefield in self.timefields:
                if timefield in user and user[timefield]:
                    user[timefield] = user[timefield].strftime(self.timestamp)
            
            # Clean the user object
            for k in self.clean:
                del user[k]
            
            # Merge enhanced attributes
            user.update({
                'groups': self.get_groups(user['uuid']),
                'is_admin': self.is_admin(user['uuid']),
                'api_key': LENSE.OBJECTS.USER.get_key(user['uuid']),
                'api_token': LENSE.OBJECTS.USER.get_token(user['uuid'])
            })
        
        # Return the constructed user results
        return users