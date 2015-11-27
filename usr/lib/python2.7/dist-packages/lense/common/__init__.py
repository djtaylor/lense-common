__version__ = '0.1.1'

# Python Libraries
import re
import json
from feedback import Feedback
from sys import getsizeof, path
from importlib import import_module

# Lense Libraries
from lense.common import config
from lense.common import logger
from lense.common.http import HEADER
from lense import MODULE_ROOT, DROPIN_ROOT
from lense.common.objects import JSONObject
from lense.common.collection import Collection
from lense.common.project import LenseProject
from lense.common.vars import PROJECTS, TEMPLATES
from lense.common.request import LenseRequestObject
from lense.common.exceptions import InvalidProjectID
from lense.common.objects.manager import ObjectsManager

# Drop-in Python path
path.append(DROPIN_ROOT)

class LenseUser(object):
    """
    User abstraction class.
    """
    def __init__(self, project, log):
        
        # Internal import
        from lense.common.objects.user.models import APIUser
        from lense.engine.api.auth import AuthAPIKey, AuthAPIToken
        from django.contrib.auth import authenticate, login, logout
        
        # Lense user model
        self._model        = APIUser
        
        # Authentication classes
        self._auth_key     = AuthAPIKey
        self._auth_token   = AuthAPIToken
        
        # Django methods
        self._authenticate = authenticate
        self._login        = login
        self._logout       = logout
        
        # Project ID / logger
        self._project      = project
        self._log          = log
    
        # Most recent authentication error
        self.AUTH_ERROR = 'An unknown authentication error occurred'
    
    def _authenticate_engine_key(self, user, key):
        """
        Perform API key authentication.
        
        :param user: The API user to authenticate
        :type  user: str
        :param  key: The user's API request key
        :type   key: str
        """
        if not self._auth_key.validate(user, key):
            return False
    
    def _authenticate_engine_token(self, user, token):
        """
        Perform API token authentication.
        
        :param  user: The API user to authenticate
        :type   user: str
        :param token: The user's API request token
        :type  token: str
        """
        if not self._auth_token.validate(user, token):
            return False
        
    def _authenticate_portal(self, user, password):
        """
        Perform API key authentication.
        
        :param     user: The API user to authenticate
        :type      user: str
        :param password: The user's request password
        :type  password: str
        """
        auth = self._authenticate(username=user, password=password)
        
        # Username/password incorrect
        if not auth:
            self.AUTH_ERROR = self._log.error('Failed to authenticate user "{0}", invalid username/password'.format(user))
            return False

        # Authorization OK
        self._log.info('Authenticated user: {0}'.format(user))
        return True
        
    def _member_of(self, user, group):
        """
        Make sure a user is a member of the request group.
        
        :param  user: The username to check
        :type   user: str
        :param group: The group name to verify membership for
        :type  group: str
        """
        
        # Make sure the group exists and the user is a member
        is_member = False
        for _group in self._model.objects.filter(username=user).values()[0]['groups']:
            if _group['uuid'] == group:
                is_member = True
                break
        
        # If the user is not a member of the group
        if not is_member:
            self.AUTH_ERROR = self._log.error('User account "{0}" is not a member of the request group: {1}'.format(user, group))
            return False
        
        # Membership is valid
        return True
        
    def GET(self, user, get_object=True):
        """
        User factory method.
        
        :param user:       The username to retrieve
        :type  user:       str
        :param get_object: If the user exists and set to true, return the user object
        """
        if self._model.objects.filter(username=user).count():
            if get_object:
                return self._model.objects.get(username=user)
            return True
            
        # User doesn't exist
        self._log.error('User "{0}" not found in database'.format(user))
        return None
    
    def LOGIN(self, request, user):
        """
        Log in the user.
        
        :param request: The Django request object to authenticate against
        :type  request: HttpRequest
        :param    user: The username to login
        :type     user: str
        """
        try:
            self._login(request, user)
            self._log.info('Logged in user: {0}'.format(user))
            return True
        
        # Failed to log in user
        except Exception as e:
            self._log.exception('Failed to log in user "{0}": {1}'.format(user, str(e)))
        
    def LOGOUT(self, request):
        """
        Log out the user.
        
        :param request: The Django request object
        :type  request: HttpRequest
        """
        try:
            self._logout(request)
            self._log.info('Logged out user: {0}'.format(user))
            return True
        
        # Failed to log out user
        except Exception as e:
            self._log.exception('Failed to log out user "{0}": {1}'.format(user, str(e)))
            return False
        
    def AUTHENTICATE(self, user, password=None, key=None, token=None, group=None):
        """
        Attempt to authenticate the user
        
        :param user:     The username to authenticate
        :type  user:     str
        :param password: The user's password (portal)
        :type  password: str
        :param      key: The user's API key (engine)
        :type       key: str
        :param    token: The user's API token (engine)
        :type     token: str
        """
        
        # Make sure the user exists
        _user = self.GET(user)
        
        # User doesn't exist
        if not _user:
            return False
        
        # Is the user active
        if not _user.is_active:
            self.AUTH_ERROR = self._log.error('User account "{0}" is disabled'.format(user))
            return False
        
        # Portal authentication
        if self._project.upper() == 'PORTAL':
            return self._authenticate_portal(user, password)

        # Engine authentication
        if self._project.upper() == 'ENGINE':
            
            # Validate group membership
            if not self._member_of(user, group):
                return False
            
            # Check token authentication first
            if token:
                return self._authenticate_engine_token(user, token)
            
            # Key authentication
            if key:
                return self._authenticate_engine_key(user, key)

        # Authentication failed
        self._log.error('Authentication failed for user: {0}'.format(user))
        return False

class LenseModules(object):
    """
    Module helper class.
    """
    def __init__(self):
        
        # Built-in/drop-in module roots
        self.ROOT    = MODULE_ROOT
        self.DROPIN  = self._get_dropin_modules()
        self.BUILTIN = self._get_builtin_modules()
    
    def _dropin_path_map(self, rel):
        """
        Map a relative module path to the drop-in root.
        """
        return '{0}/lense_d/{1}'.format(DROPIN_ROOT, rel)
    
    def _builtin_path_map(self, rel):
        """
        Map a relative path to the built-in root.
        """
        return '{0}/{1}'.format(MODULE_ROOT, rel)
    
    def _get_dropin_modules(self):
        """
        Drop-in module attributes.
        """
        return Collection({
            'CLIENT': [self._dropin_path_map('client/module'), 'lense_d.client.module']
        }).get()
    
    def _get_builtin_modules(self):
        """
        Built-in module attributes.
        """
        return Collection({
            'CLIENT': [self._builtin_path_map('client/module'), 'lense.client.module']
        }).get()
    
    def NAME(self, file):
        """
        Extract a module name from a file path.
        """
        return re.compile(r'^([^\.]*)\..*$').sub(r'\g<1>', file)
    
    def IMPORT(self, module):
        """
        Import a built-in or drop-in module.
        """
        return import_module(module)

class LenseCommon(object):
    """
    Common class for creating project specific instances of common libraries,
    variables, and modules.
    """
    def __init__(self, project):
        
        # Get the project attributes
        self.PROJECT     = LenseProject(project)
        
        """
        Project Objects
        
        COLLECTION: Immutable collection generator
        REQUEST:    Generate a request object or not
        LOG:        Create the log handler if needed
        OBJECTS:    Create the object manager if needed
        USER:       User handler
        CONF:       The projects configuration
        MODULE:     The module helper
        JSON:       JSON object manager
        INVALID:    Error relay
        VALID:      Success relay 
        FEEDBACK:   CLI feedback handler
        """
        self.COLLECTION  = Collection
        self.REQUEST     = self._requires('get_request', LenseRequestObject, [self.PROJECT])
        self.LOG         = self._requires('get_logger', logger.create_project(), [project])
        self.OBJECTS     = self._requires('get_objects', ObjectsManager)
        self.USER        = self._requires('get_user', LenseUser, [self.PROJECT.name, self.LOG])
        self.CONF        = self._requires('get_conf', config.parse, [project])
        self.MODULE      = LenseModules()
        self.JSON        = JSONObject()
        self.FEEDBACK    = Feedback()
        
    def _requires(self, key, obj, args=[], kwargs={}):
        """
        Load the return object if the project requires it.
        
        :param    key: The boolean attribute to check
        :type     key: str
        :param    obj: The object to return
        :type     obj: object
        :param   args: Arguments to pass to the object
        :type    args: list
        :param kwargs: Keyword arguments to pass to the object
        :type  kwargs: dict
        """
        if getattr(self.PROJECT, key, False):
            return obj(*args, **kwargs)
        return None