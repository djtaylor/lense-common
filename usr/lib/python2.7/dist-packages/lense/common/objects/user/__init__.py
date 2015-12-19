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
        
    def grant_key(self, uuid, api_key=rstring(64), overwrite=False):
        """
        Grant an API key to a user account.
        
        :param      uuid: The UUID of the user to grant the key
        :type       uuid: str
        :
        :param overwrite: Overwrite the existing key if one exists.
        :type  overwrite: bool
        :rtype: bool
        """
        
        # Get the user object
        user = LENSE.ensure(self.get(uuid=uuid),
            isnot = None,
            error = 'Cannot grant key to user {0}, not found'.format(uuid),
            debug = 'Retrieved user {0} object'.format(uuid),
            code  = 404)
        
        # If the user already has a key
        if self.KEY.exists(user=user.uuid):
            LENSE.ensure(overwrite,
                error = 'Cannot overwrite user {0} key without explicitly setting "overwrite" argument',
                debug = 'Overwriting user {0} API key -> {1}'.format(uuid, api_key),
                code  = 400)
            
            # Update the key
            LENSE.ensure(self.KEY.update(user=user, api_key=api_key),
                error = 'Failed to update user {0} API key'.format(uuid),
                debug = 'Updated user {0} API key -> {1}'.format(uuid, api_key),
                code  = 500)
        
        # Grant a new key
        else:
            LENSE.ensure(self.KEY.create(user=user, api_key=api_key),
                error = 'Failed to create user {0} API key'.format(uuid),
                debug = 'Created user {0} API key -> {1}'.format(uuid, api_key),
                code  = 500)
        return api_key
    
    def grant_token(self, uuid, token=rstring(255), overwrite=False):
        """
        Create or set a user's token.
        
        :param    user: User search string
        :type     user: str
        :param   token: The token string
        :type    token: str
        """
        expires = datetime.now() + timedelta(hours=settings.API_TOKEN_LIFE)
        
        # Get the user object
        user = LENSE.ensure(self.get(uuid=uuid),
            isnot = None,
            error = 'Cannot grant token to user {0}, not found'.format(uuid),
            debug = 'Retrieved user {0} object'.format(uuid),
            code  = 404)
        
        # If the user already has a token
        if self.TOKEN.exists(user=user.uuid):
            LENSE.ensure(overwrite,
                error = 'Cannot overwrite user {0} token without explicitly setting "overwrite" argument',
                debug = 'Overwriting user {0} API token -> {1}'.format(uuid, api_key),
                code  = 400)
            
            # Update the token
            LENSE.ensure(self.TOKEN.update(user=user, token=token, expires=expires),
                error = 'Failed to update user {0} API token'.format(uuid),
                debug = 'Updated user {0} API token -> {1}'.format(uuid, token),
                code  = 500)
        
        # Grant a new token
        else:
            LENSE.ensure(self.TOKEN.create(user=user, token=token, expires=expires),
                error = 'Failed to create user {0} API token'.format(uuid),
                debug = 'Created user {0} API token -> {1}'.format(uuid, token),
                code  = 500)
        return token
    
    def member_of(self, user, group):
        """
        Make sure a user is a member of the request group.
        
        :param  user: The username/UUID to check
        :type   user: str
        :param group: The group name to verify membership for
        :type  group: str
        """
        is_member = False
        for _group in getattr(self.get(**self.map_user(user)), 'groups', []):
            if _group['uuid'] == group: 
                is_member = True
                break
        return is_member
    
    def ensure(self, attr, exc=None, msg=None, args=[], kwargs={}):
        """
        Ensure a user attribute is true.
        
        :param attr: The attribute key to check
        :type  attr: str
        :param  exc: Optional exception class to raise if the check fails
        :type   exc: object
        :param  msg: Optional exception message to raise
        :type   msg: str
        :rtype: bool
        """
        user_attr = getattr(self, attr, None)
        error_msg = 'Failed to ensure user attribute: {0}=False'.format(attr)
        
        # Is the attribute callable
        if callable(user_attr):
            attr_val = user_attr(*args, **kwargs)
            
            # Attribute return value is false
            if not attr_val:
                if exc:
                    raise exc(error_msg)
                return False
        
        # Attribute not found or is false
        if not user_attr:
            if exc:
                raise exc(error_msg)
            return False
        
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
            self.ensure('exists', exc=AuthError, msg='User "{0}" does not exist'.format(user), kwargs=self.map_user(user))       
            self.ensure('active', exc=AuthError, msg='User "{0}" is inactive'.format(user), kwargs=self.map_user(user))
            
            # Portal authentication
            if LENSE.PROJECT.name.upper() == 'PORTAL':
                return LENSE.AUTH.PORTAL(user, set_arg(passwd, LENSE.REQUEST.USER.passwd))
    
            # Engine authentication
            if LENSE.PROJECT.name.upper() == 'ENGINE':
                
                # Get the user group
                group = set_arg(group, LENSE.REQUEST.USER.group)
                
                # Make sure the user is a group member
                self.ensure('member_of', 
                    exc  = AuthError, 
                    msg  = 'User "{0}" is not a member of group: {1}'.format(user, group), 
                    args = [user, group]
                )
                
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