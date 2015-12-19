from uuid import UUID

# Lense Libraries
from lense.common.utils import rstring
from lense import import_class, set_arg
from lense.common.exceptions import AuthError

class LenseUser(object):
    """
    User abstraction class.
    """
    def __init__(self):
        self.model         = import_class('APIUser', 'lense.common.objects.user.models', init=False)
        
        # Django methods
        self._login        = import_class('login', 'django.contrib.auth', init=False)
        self._logout       = import_class('logout', 'django.contrib.auth', init=False)
        
        # Internal models
        self._token        = import_class('APIUserTokens', 'lense.common.objects.user.models', init=False)
        self._key          = import_class('APIUserKeys', 'lense.common.objects.user.models', init=False)
        
    def _filter(self, user):
        """
        Map a user name or UUID to filter parameters.
        
        :param user: User name or UUID
        :type  user: str
        :rtype: dict
        """
        try:
            UUID(user, version=4)
            return {'uuid': user}
        except ValueError:
            return {'username': user}
        
    def member_of(self, user, group):
        """
        Make sure a user is a member of the request group.
        
        :param  user: The username to check
        :type   user: str
        :param group: The group name to verify membership for
        :type  group: str
        """
        is_member = False
        for _group in getattr(self.get(**self._filter(user)), 'groups', []):
            if _group['uuid'] == group: 
                is_member = True
                break
        return is_member
        
    def key(self, user=None):
        """
        Get the current API key for a user account.
        
        :param user: Optional user search string
        :type  user: str
        :rtype: str
        """
        _user = self.get(**self._filter(set_arg(user, LENSE.REQUEST.USER.name)))
        
        # Get the API key
        key = self._key.objects.get(user=_user.uuid)
        
        # Return the API token if it exists
        return None if not key else key.api_key
        
    def token(self, user=None):
        """
        Get the current API token for a user account.
        
        :param user: Optional user search string
        :type  user: str
        :rtype: str
        """
        _user = self.get(**self._filter(set_arg(user, LENSE.REQUEST.USER.name)))
        
        # Get the API token
        token = self._token.objects.get(user=_user.uuid)

        # Return the API token if it exists
        return None if not token else token.api_token
        
    def set_token(self, user, token, expires):
        """
        Create or set a user's token.
        
        :param    user: User search string
        :type     user: str
        :param   token: The token string
        :type    token: str
        :param expires: Token expiration timestamp
        :type  expires: str
        """
        self._token(id=None, user=user, token=token, expires=expires).save()
        
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
        
    def active(self, user):
        """
        Check if a user account is acive:
        
        :param user: The username to check
        :type  user: str
        :rtype: bool
        """
        return getattr(self.get(**self._filter(user)), 'is_active', False)
        
    def exists(self, **kwargs):
        """
        Check if a user exists by username or UUID
        
        :param user: The username or UUID to check
        :type  user: str
        :rtype: bool
        """
        if self.model.objects.filter(**kwargs).count():
            return True
        return False
        
    def get(self, **kwargs):
        """
        User factory method.
        
        :param    user: The username/UUID to retrieve
        :type     user: str
        :rtype: APIUser|None
        """
        if self.exists(**kwargs):
            return self.model.objects.get(**kwargs)
        return None
    
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
            self.ensure('exists', exc=AuthError, msg='User "{0}" does not exist'.format(user), args=[user])       
            self.ensure('active', exc=AuthError, msg='User "{0}" is inactive'.format(user), args=[user])
            
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