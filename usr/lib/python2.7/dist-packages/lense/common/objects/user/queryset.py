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

        # API key / token
        self.api_key = import_class('APIUserKeys', 'lense.common.objects.user.models', init=False)
        self.api_token = import_class('APIUserTokens', 'lense.common.objects.user.models', init=False)

    def get_key(self, user):
        """
        Get the API key for a user.
        """
        if self.api_key.objects.filter(user=user).count():
            return self.api_key.objects.get(user=user).api_key
        return None
    
    def get_token(self, user):
        """
        Get the API key for a user.
        """
        if self.api_token.objects.filter(user=user).count():
            return self.api_token.objects.get(user=user).token
        return None

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
                'api_key': self.get_key(user['uuid']),
                'api_token': self.get_token(user['uuid'])
            })
        
        # Return the constructed user results
        return users