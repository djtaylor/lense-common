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
        
        # Authentication attributes
        self.auth_error = None
        
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
            self.log('Extending user {0} attributes -> {1}={2}'.format(user.uuid,k,v), level='debug', method='extend')
            setattr(user, k, v)
        return user
        
    def get(self, *args, **kwargs):
        """
        Retrieve an object definition.
        """
        if args:
            kwargs = {'uuid': self.get_uuid(args[0])}
            
            # User doesn't exist
            if not self.exists(**filter):
                self.log('Object not found -> filter: {0}'.format(str(filter)), level='debug', method='get')
                return None
            
            # Get the user object
            user = self.model.objects.get(**filter)
            self.log('Retrieved object -> filter: {0}'.format(str(filter)), level='debug', method='get')
            return self.extend(user)
        
        # Retrieving all
        if not kwargs:
            all_users = list(self.model.objects.all())
            self.log('Retrieved all objects: count={1}'.format(self.cls, all_users.count()), level='debug', method='get')
            for user in all_users:
                self.extend(user)
            return all_users
    
        # User doesn't exist
        if not self.exists(**kwargs):
            self.log('Object not found -> filter: {0}'.format(str(kwargs)), level='debug', method='get')
            return None
    
        # Retrieving by parameters
        user = self.model.objects.get(**kwargs)
        self.log('Retrieved object -> filter: {0}'.format(str(kwargs)), level='debug', method='get')
        return self.extend(user)
        
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
        
        :param      user: The APIUser object to grant a key for
        :type       user: APIUser
        :param overwrite: Overwrite the existing key if one exists.
        :type  overwrite: bool
        :rtype: bool
        """
        key  = rstring(64)
        
        # Must be an APIUser instance
        if not isinstance(user, self.model):
            raise Exception('User argument must be an instance of APIUser')
        
        # If the user already has a key
        if self.KEY.exists(user=user.uuid):
            LENSE.ensure(overwrite,
                error = 'Cannot overwrite user {0} key without explicitly setting "overwrite" argument'.format(user.uuid),
                debug = 'Overwriting user {0} API key -> {1}'.format(user.uuid, key),
                code  = 400)
            
            # Update the key
            LENSE.ensure(self.KEY.update(user=user, key=key),
                error = 'Failed to update user {0} API key'.format(user.uuid),
                debug = 'Updated user {0} API key -> {1}'.format(user.uuid, key),
                code  = 500)
        
        # Grant a new key
        else:
            LENSE.ensure(self.KEY.create(user=user, key=key),
                error = 'Failed to create user {0} API key'.format(user.uuid),
                debug = 'Created user {0} API key -> {1}'.format(user.uuid, key),
                code  = 500)
        return key
    
    def grant_token(self, user, overwrite=False):
        """
        Create or set a user's token.
        
        :param    user: The APIUser object to grant a token for
        :type     user: APIUser
        :param   token: The token string
        :type    token: str
        """
        token   = rstring(255)
        expires = datetime.now() + timedelta(hours=settings.API_TOKEN_LIFE)
        
        # Must be an APIUser instance
        if not isinstance(user, self.model):
            raise Exception('User argument must be an instance of APIUser')
        
        # If the user already has a token
        if self.TOKEN.exists(user=user.uuid):
            LENSE.ensure(overwrite,
                error = 'Cannot overwrite user {0} token without explicitly setting "overwrite" argument'.format(user.uuid),
                debug = 'Overwriting user {0} API token -> {1}'.format(user.uuid, api_key),
                code  = 400)
            
            # Update the token
            LENSE.ensure(self.TOKEN.update(user=user, token=token, expires=expires),
                error = 'Failed to update user {0} API token'.format(user.uuid),
                debug = 'Updated user {0} API token -> {1}'.format(user.uuid, token),
                code  = 500)
        
        # Grant a new token
        else:
            LENSE.ensure(self.TOKEN.create(user=user, token=token, expires=expires),
                error = 'Failed to create user {0} API token'.format(user.uuid),
                debug = 'Created user {0} API token -> {1}'.format(user.uuid, token),
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
        if LENSE.OBJECTS.GROUP.MEMBERS.exists(member=uuid):
            user_groups = LENSE.OBJECTS.GROUP.MEMBERS.get(member=uuid)
            
            # Single group
            if not isinstance(user_groups, list):
                groups.append(user_groups.group)
            
            # Multiple groups
            else:
                for group in user_groups:
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
        return False if not group in groups else True
        
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
            self.auth_error = str(e.message)
            LENSE.LOG.error('Failed to authenticate user "{0}": {0}'.format(user, str(e)))