from uuid import uuid4

# Django Libraries
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager

# Lense Libraries
from lense.common.vars import GROUPS
from lense.common.objects.user.queryset import APIUserQuerySet

class APIUserManager(BaseUserManager):
    """
    Custom user manager for the custom user model.
    """
    def get_queryset(self, *args, **kwargs):
        """
        Wrapper method for the internal get_queryset() method.
        """
        return APIUserQuerySet(model=self.model)
        
    def get_or_create(self, *args, **kwargs):
        """
        Get or create a new user object.
        """
        
        # Get the user queryset
        queryset = self.get_queryset()
        
        # If the user exists
        if queryset.filter(username=kwargs['username']).count():
            return queryset.get(username=kwargs['username']), False
        
        # User doesn't exist yet
        user = self.create_user(*args, **kwargs)
        
        # Return the created user
        return user, True
        
    def create_user(self, group=GROUPS.DEFAULT.UUID, uuid=None, **attrs):
        """
        Create a new user account.
        """
        
        # Fix circular imports
        from lense.engine.api.auth import AuthAPIKey
        from lense.common.objects.group.models import APIGroups
        from lense.common.objects.user.models import APIUserKeys
        
        # Required attributes
        for k in ['username', 'email', 'password']:
            if not k in attrs:
                raise Exception('Failed to create user, missing required attribute: {0}'.format(k))
        
        # Get the current timestamp
        now = timezone.now()
        
        # Generate a unique ID for the user
        user_uuid = str(uuid4())
        
        # If manually specifying a UUID
        if uuid:
            user_uuid = uuid
        
        # Update the user creation attributes
        attrs.update({
            'uuid':        user_uuid,
            'is_active':   True,
            'last_login':  now,
            'date_joined': now
        })
        # Create a new user object
        user = self.model(**attrs)
        
        # Set the password and and save
        user.set_password(attrs['password'])
        user.save(using=self._db)
        
        # Get the group object
        group = APIGroups.objects.get(uuid=group)
        
        # Add the user to the group
        group.members_set(user)
        
        # Generate an API key for the user
        api_key = APIUserKeys(user=user, api_key=AuthAPIKey.create()).save()
        
        # Return the user object
        return user