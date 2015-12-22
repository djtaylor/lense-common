from datetime import datetime, timedelta

# Django Libraries
from django.conf import settings

# Lense Libraries
from lense import import_class, set_arg
from lense.common.utils import rstring
from lense.common.exceptions import AuthError
from lense.common.objects.base import LenseBaseObject

class ObjectInterface(LenseBaseObject):
    def __init__(self):
        super(ObjectInterface, self).__init__('lense.common.objects.user.models', 'APIUser')
        
        # Django methods
        self._login  = import_class('login', 'django.contrib.auth', init=False)
        self._logout = import_class('logout', 'django.contrib.auth', init=False)
        
        # User key and token handlers
        self.KEY     = LenseBaseObject('lense.common.objects.user.models', 'APIUserKeys')
        self.TOKEN   = LenseBaseObject('lense.common.objects.user.models', 'APIUserTokens')
        
    def extend(self, user):
        """
        Construct extended user attributes.
        
        :param user: The user object to extend
        :type  user: APIUser
        :rtype: APIUser
        """
        for k,v in {
            'api_key': self.get_key(user.uuid),
            'api_token': self.get_token(user.uuid),
            'groups': self.get_groups(user.uuid)
        }.iteritems():
            setattr(user, k, v)
        
    def get(self, *args, **kwargs):
        """
        Retrieve an object definition.
        """
        if args:
            uuid = self.get_uuid(args[0])
            return self.extend(self.model.objects.get(uuid=uuid))
        
        # Retrieving all
        if not kwargs:
            all_users = list(self.model.objects.all())
            for user in all_users:
                self.extend(user)
            return all_users
    
        # Retrieving by parameters
        return self.extend(self.model.objects.get(**kwargs))
        
    def get_uuid(self, user):
        """
        Retrieve a user's UUID from various attributes.
        
        :param user: The user string to map to UUID
        :type  user: str
        :rtype: str
        """
        if self.is_uuid(user):
            return user
        
        # Email address
        if self.is_email(user):
            user_obj = LENSE.ensure(LENSE.OBJECTS.USER.get(email=user),
                isnot = None,
                error = 'User not found for email {0}'.format(user),
                debug = 'Mapped user email {0} to UUID'.format(user),
                code  = 404)
            return user_obj.uuid
        
        # Else try username
        user_obj = LENSE.ensure(LENSE.OBJECTS.USER.get(username=user),
            isnot = None,
            error = 'User not found for username {0}'.format(user),
            debug = 'Mapped username {0} to UUID'.format(user),
            code  = 404)
        return user_obj.uuid
        
    def get_key(self, user):
        """
        Retrieve an API key for a user account.
        
        :param user: The username or UUID to look for
        :type  user: str
        :rtype: str
        """
        uuid = self.get_uuid(user)
        
        # Does the user have a key entry
        if self.KEY.filter(user=uuid).count():
            user = LENSE.ensure(self.KEY.get(user=uuid),
                error = 'Could not find user {0} API key'.format(uuid),
                debug = 'Retrieved user {0} API key object'.format(uuid),
                code  = 404)
            return user.key
        
        # User has no key
        return None
        
    def get_token(self, user):
        """
        Retrieve an API token for a user account.
        
        :param user: The username or UUID to look for
        :type  user: str
        :rtype: str
        """
        uuid = self.get_uuid(user)
        
        # Does the user have a token entry
        if self.TOKEN.filter(user=uuid).count():
            user = LENSE.ensure(self.TOKEN.get(user=uuid),
                error = 'Could not find user {0} API token'.format(uuid),
                debug = 'Retrieved user {0} API token object'.format(uuid),
                code  = 404)
            return user.token
        
        # User has no token
        return None
        
    def grant_key(self, user, overwrite=False):
        """
        Grant an API key to a user account.
        
        :param      uuid: The UUID of the user to grant the key
        :type       uuid: str
        :param overwrite: Overwrite the existing key if one exists.
        :type  overwrite: bool
        :rtype: bool
        """
        uuid = self.get_uuid(user)
        key  = rstring(64)
        
        # Get the user object
        user = LENSE.ensure(self.get(uuid=uuid),
            isnot = None,
            error = 'Cannot grant key to user {0}, not found'.format(uuid),
            debug = 'Retrieved user {0} object'.format(uuid),
            code  = 404)
        
        # If the user already has a key
        if self.KEY.exists(user=uuid):
            LENSE.ensure(overwrite,
                error = 'Cannot overwrite user {0} key without explicitly setting "overwrite" argument',
                debug = 'Overwriting user {0} API key -> {1}'.format(uuid, key),
                code  = 400)
            
            # Update the key
            LENSE.ensure(self.KEY.update(user=uuid, key=key),
                error = 'Failed to update user {0} API key'.format(uuid),
                debug = 'Updated user {0} API key -> {1}'.format(uuid, key),
                code  = 500)
        
        # Grant a new key
        else:
            LENSE.ensure(self.KEY.create(user=uuid, key=key),
                error = 'Failed to create user {0} API key'.format(uuid),
                debug = 'Created user {0} API key -> {1}'.format(uuid, key),
                code  = 500)
        return api_key
    
    def grant_token(self, user, overwrite=False):
        """
        Create or set a user's token.
        
        :param    user: User search string
        :type     user: str
        :param   token: The token string
        :type    token: str
        """
        uuid    = self.get_uuid(user)
        token   = rstring(255)
        expires = datetime.now() + timedelta(hours=settings.API_TOKEN_LIFE)
        
        # Get the user object
        user = LENSE.ensure(self.get(uuid=uuid),
            isnot = None,
            error = 'Cannot grant token to user {0}, not found'.format(uuid),
            debug = 'Retrieved user {0} object'.format(uuid),
            code  = 404)
        
        # If the user already has a token
        if self.TOKEN.exists(user=uuid):
            LENSE.ensure(overwrite,
                error = 'Cannot overwrite user {0} token without explicitly setting "overwrite" argument',
                debug = 'Overwriting user {0} API token -> {1}'.format(uuid, api_key),
                code  = 400)
            
            # Update the token
            LENSE.ensure(self.TOKEN.update(user=uuid, token=token, expires=expires),
                error = 'Failed to update user {0} API token'.format(uuid),
                debug = 'Updated user {0} API token -> {1}'.format(uuid, token),
                code  = 500)
        
        # Grant a new token
        else:
            LENSE.ensure(self.TOKEN.create(user=uuid, token=token, expires=expires),
                error = 'Failed to create user {0} API token'.format(uuid),
                debug = 'Created user {0} API token -> {1}'.format(uuid, token),
                code  = 500)
        return token
    
    def get_groups(self, user):
        """
        Retrieve a list of user groups.
        
        :param  user: The user to retrieve groups for
        :type   user: str
        :rtype: list
        """
        uuid   = self.get_uuid(user)
        groups = []
        
        # Is the user a member of any groups
        if LENSE.OBJECTS.GROUP.MEMBERS.filter(member=uuid).count():
            for group in list(LENSE.OBJECTS.GROUP.MEMBERS.get(member=uuid)):
                groups.append(group.group)
        return groups
    
    def member_of(self, user, group):
        """
        Make sure a user is a member of the request group.
        
        :param  user: The username/UUID to check
        :type   user: str
        :param group: The group name to verify membership for
        :type  group: str
        """
        groups = self.get_groups(user)
        
        is_member = False
        for _group in getattr(self.get(**self.map_user(user)), 'groups', []):
            if _group['uuid'] == group: 
                is_member = True
                break
        return is_member
        
    def active(self, **kwargs):
        """
        Check if a user account is acive:
        
        :param user: The username to check
        :type  user: str
        :rtype: bool
        """
        return getattr(self.get(**kwargs), 'is_active', False)
    
    def login(self, request=None, user=None):
        """
        Login a portal user.
        
        :param request: The Django request object
        :type  request: HttpRequest
        :param    user: The user to login
        :type     user: str
        """
        try:
            
            # Request object / username
            request = set_arg(request, LENSE.REQUEST.DJANGO)
            user    = set_arg(user, LENSE.REQUEST.USER.name)
            
            # Login the user
            self._login(request, user)
            LENSE.LOG.info('Logged in user: {0}'.format(user))
            return True
        
        # Failed to log in user
        except Exception as e:
            LENSE.LOG.exception('Failed to log in user "{0}": {1}'.format(user, str(e)))
            return False
        
    def logout(self, request=None, user=None):
        """
        Log out the user.
        
        :param request: The Django request object
        :type  request: HttpRequest
        :param    user: The user to logout
        :type     user: str
        """
        try:
            
            # Request object / username
            request = set_arg(request, LENSE.REQUEST.DJANGO)
            user    = set_arg(user, LENSE.REQUEST.USER.name)
            
            # Logout the user
            self._logout(request)
            LENSE.LOG.info('Logged out user: {0}'.format(user))
            return True
        
        # Failed to log out user
        except Exception as e:
            LENSE.LOG.exception('Failed to log out user "{0}": {1}'.format(user, str(e)))
            return False
        
    def authenticate(self, user=None, passwd=None, group=None, key=None, token=None):
        """
        Attempt to authenticate the user.
        
        :param   user: The user to authenticate
        :type    user: str
        :param passwd: The user's attempted password
        :type  passwd: str
        :param  group: The user's group
        :type   group: str
        :param    key: The user's attempted API key
        :type     key: str
        :param  token: The user's attempted API token
        :type   token: str
        """
        try:
            
            # Target user
            user   = set_arg(user, LENSE.REQUEST.USER.name)
            
            # User does not exist / is inactive
            LENSE.ensure(self.exists(uuid=self.get_uuid(user)),
                error = 'User {0} does not exist'.format(user),
                debug = 'Found user for {0}, checking state'.format(user),
                code  = 404)
            LENSE.ensure(self.active(uuid=self.get_uuid(user)),
                error = 'User {0} does not exist'.format(user),
                debug = 'User {0} is active, authenticating'.format(user),
                code  = 404)
            
            # Portal authentication
            if LENSE.PROJECT.name.upper() == 'PORTAL':
                return LENSE.AUTH.PORTAL(user, set_arg(passwd, LENSE.REQUEST.USER.passwd))
    
            # Engine authentication
            if LENSE.PROJECT.name.upper() == 'ENGINE':
                
                # Get the user group
                group = set_arg(group, LENSE.REQUEST.USER.group)
                
                # Make sure the user is a group member
                LENSE.ensure(self.member_of(user, group),
                    error = 'User {0} is not a member of group {1}'.format(user, group),
                    debug = 'User {0} is a member of group {1}'.format(user, group),
                    code  = 400)
                
                # Token / key authentication
                token = set_arg(token, LENSE.REQUEST.token)
                key   = set_arg(key, LENSE.REQUEST.key)
                
                # Check token authentication first
                if token:
                    return LENSE.AUTH.TOKEN(user, token)
                
                # Key authentication
                if key:
                    return LENSE.AUTH.KEY(user, key)
            
        # Failed to authenticate user
        except AuthError as e:
            return LENSE.AUTH.set_error(
                LENSE.LOG.error('Failed to authenticate user "{0}": {0}'.format(user, str(e)))
            )