# Lense Libraries
from lense import import_class
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
        self._key          = import_class('APIUserKeys', 'lense.common.objects.user.modles', init=False)
        
    def member_of(self, user, group):
        """
        Make sure a user is a member of the request group.
        
        :param  user: The username to check
        :type   user: str
        :param group: The group name to verify membership for
        :type  group: str
        """
        
        # Make sure the group exists and the user is a member
        is_member = False
        for _group in self.model.objects.filter(username=user).values()[0]['groups']:
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
        _user = self.get(user if user else LENSE.REQUEST.user.name)
        
        # Get the API key
        api_key = list(self._key.objects.filter(user=_user.uuid).values())
        
        # Return the API token if it exists
        return None if not api_key else api_key[0]['api_key']
        
    def token(self, user=None):
        """
        Get the current API token for a user account.
        
        :param user: Optional user search string
        :type  user: str
        :rtype: str
        """
        _user = self.get(user if user else LENSE.REQUEST.user.name)
        
        # Get the API token
        api_token = list(self._token.objects.filter(user=_user.uuid).values())

        # Return the API token if it exists
        return None if not api_token else api_token[0]['api_token']
        
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
        return getattr(self.get(user), 'is_active', False)
        
    def exists(self, user):
        """
        Check if a user exists by username or UUID
        
        :param user: The username or UUID to check
        :type  user: str
        :rtype: bool
        """
        if self.model.objects.filter(uuid=user).count():
            return True
            
        if self.model.objects.filter(username=user).count():
            return True
            
        # User does not exists
        return False
        
    def get(self, user, get_object=True):
        """
        User factory method.
        
        :param user:       The username to retrieve
        :type  user:       str
        :param get_object: If the user exists and set to true, return the user object
        """
        if self.exists(user):
            if get_object:
                return self.model.objects.get(username=user)
            return True
            
        # User doesn't exist
        LENSE.LOG.error('User "{0}" not found in database'.format(user))
        return None
    
    def login(self):
        """
        Login a portal user.
        """
        try:
            
            # Request object / username
            request = LENSE.REQUEST.DJANGO
            user    = LENSE.REQUEST.USER.name
            
            # Login the user
            self._login(request, user)
            LENSE.LOG.info('Logged in user: {0}'.format(user))
            return True
        
        # Failed to log in user
        except Exception as e:
            LENSE.LOG.exception('Failed to log in user "{0}": {1}'.format(user, str(e)))
            return False
        
    def logout(self):
        """
        Log out the user.
        """
        try:
            
            # Request object / username
            request = LENSE.REQUEST.DJANGO
            user    = LENSE.REQUEST.USER.name
            
            # Logout the user
            self._logout(request)
            LENSE.LOG.info('Logged out user: {0}'.format(user))
            return True
        
        # Failed to log out user
        except Exception as e:
            LENSE.LOG.exception('Failed to log out user "{0}": {1}'.format(user, str(e)))
            return False
        
    def authenticate(self):
        """
        Attempt to authenticate the user.
        """
        try:
            
            # Target user
            user = LENSE.REQUEST.USER.name
            
            # User does not exist / is inactive
            self.ensure('exists', exc=AuthError, msg='User "{0}" does not exist'.format(user), args=[user])       
            self.ensure('active', exc=AuthError, msg='User "{0}" is inactive'.format(user), args=[user])
            
            # Portal authentication
            if LENSE.PROJECT.name.upper() == 'PORTAL':
                return LENSE.AUTH.PORTAL(user, LENSE.REQUEST.USER.passwd)
    
            # Engine authentication
            if LENSE.PROJECT.name.upper() == 'ENGINE':
                
                # Get the user group
                group = LENSE.REQUEST.USER.group
                
                # Make sure the user is a group member
                self.ensure('member_of', 
                    exc  = AuthError, 
                    msg  = 'User "{0}" is not a member of group: {1}'.format(user, group), 
                    args = [user, group]
                )
                
                # Token / key authentication
                token = LENSE.REQUEST.token
                key   = LENSE.REQUEST.key
                
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