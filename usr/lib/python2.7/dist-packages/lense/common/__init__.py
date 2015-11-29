__version__ = '0.1.1'

# Python Libraries
import re
import json
import __builtin__
from os import listdir, path
from feedback import Feedback
from sys import getsizeof, path, modules
from importlib import import_module

# Lense Libraries
from lense import import_class
from lense.common.http import HEADER
from lense import MODULE_ROOT, DROPIN_ROOT
from lense.common.exceptions import InvalidProjectID, AuthError
from lense.common.vars import PROJECTS, TEMPLATES, HANDLERS

# Drop-in Python path
path.append(DROPIN_ROOT)
    
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
    
    def login(self, request=LENSE.REQUEST.django, user=LENSE.REQUEST.user.name):
        """
        Log in the user.
        
        :param request: The Django request object to authenticate against
        :type  request: HttpRequest
        :param    user: The username to login
        :type     user: str
        """
        try:
            self._login(request, user)
            LENSE.LOG.info('Logged in user: {0}'.format(user))
            return True
        
        # Failed to log in user
        except Exception as e:
            LENSE.LOG.exception('Failed to log in user "{0}": {1}'.format(user, str(e)))
            return False
        
    def logout(self, request=LENSE.REQUEST.django):
        """
        Log out the user.
        
        :param request: The Django request object
        :type  request: HttpRequest
        """
        try:
            self._logout(request)
            LENSE.LOG.info('Logged out user: {0}'.format(user))
            return True
        
        # Failed to log out user
        except Exception as e:
            LENSE.LOG.exception('Failed to log out user "{0}": {1}'.format(user, str(e)))
            return False
        
    def authenticate(self,
            user     = LENSE.REQUEST.user.name, 
            password = LENSE.REQUEST.user.password, 
            key      = LENSE.REQUEST.key, 
            token    = LENSE.REQUEST.token, 
            group    = LENSE.REQUEST.user.group
        ):
        """
        Attempt to authenticate the user
        
        :param     user: The username to authenticate
        :type      user: str
        :param password: The user's password (portal)
        :type  password: str
        :param      key: The user's API key (engine)
        :type       key: str
        :param    token: The user's API token (engine)
        :type     token: str
        """
        try:
            
            # User does not exist / is inactive
            self.ensure('exists', exc=AuthError, msg='User "{0}" does not exist'.format(user), args=[user])       
            self.ensure('active', exc=AuthError, msg='User "{0}" is inactive'.format(user), args=[user])
            
            # Portal authentication
            if LENSE.PROJECT.name.upper() == 'PORTAL':
                return LENSE.AUTH.PORTAL(user, password)
    
            # Engine authentication
            if LENSE.PROJECT.name.upper() == 'ENGINE':
                self.ensure('member_of', 
                    exc  = AuthError, 
                    msg  = 'User "{0}" is not a member of group: {1}'.format(user, group), 
                    args = [user, group]
                )
                
                # Check token authentication first
                if token:
                    return LENSE.AUTH.TOKEN(user, token)
                
                # Key authentication
                if key:
                    return LENSE.AUTH.KEY(user, key)
            
        # Failed to authenticate user
        except AuthError as e:
            return LENSE.AUTH.set_error(
                LENSE.LOG.error('Failed to authenticate user: {0}'.format(str(e)))
            )

class LenseModules(object):
    """
    Module helper class.
    """
    def __init__(self):
        
        # Built-in/drop-in module roots
        self.root     = MODULE_ROOT
        self.dropin   = self._get_dropin_modules()
        self.builtin  = self._get_builtin_modules()
    
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
    
    def handlers(self, ext=None, load=None):
        """
        Return handlers for a project.
        
        :param  ext: Handler extension (nested handlers)
        :type   ext: str
        :param load: Return instances of the handlers objects
        :type  load: str
        """
        
        # Project handler attributes / handler objects / handler extension
        handler_attrs = getattr(HANDLERS, LENSE.PROJECT.name)
        handler_objs  = {} if load else []
        
        # Scan every handler
        for handler in listdir(handler_attrs.DIR):
            
            # Ignore special files
            if re.match(r'^__.*$', handler) or re.match(r'^.*\.pyc$', handler):
                continue
            
            # Handler file path / Python path
            handler_file = '{0}/{1}{2}'.format(handler_attrs.DIR, handler, ('.py' if not ext else '/{0}.py'.format(ext)))
            handler_mod  = '{0}.{1}{2}'.format(handler_attrs.MOD, handler, ('' if not ext else '.{0}'.format(ext)))
            
            # If loading the handler objects
            if load:
                mod_obj = import_module(handler_mod)
                
                # Handler class not found
                if not hasattr(mod_obj, load):
                    handler_objs[handler] = None
            
                # Load the handler class
                handler_objs[handler] = getattr(mod_obj, load)
            
            # Returning handler attributes
            else:
                handler_objs.append({
                    'name': handler,
                    'file': handler_file,
                    'mod':  handler_mod                         
                })
        
        # Return the constructed handlers object
        return handler_objs
    
    def name(self, file):
        """
        Extract a module name from a file path.
        """
        return re.compile(r'^([^\.]*)\..*$').sub(r'\g<1>', file)
    
    def imp(self, module):
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
        self.PROJECT     = import_class('LensePoject', 'lense.common', [project])
        
        # Get project attribute
        def pattr(a):
            return getattr(self.PROJECT, a, False)
        
        """
        Project Objects
        
        COLLECTION: Immutable collection generator
        REQUEST:    Generate a request object or not
        LOG:        Create the log handler if needed
        OBJECTS:    Create the object manager if needed
        USER:       User handler
        CONF:       The projects configuration
        API:        API base constructor
        MODULE:     The module helper
        JSON:       JSON object manager
        INVALID:    Error relay
        VALID:      Success relay 
        FEEDBACK:   CLI feedback handler
        """
        self.COLLECTION  = import_class('Collection', 'lense.common.collection', init=False)
        self.AUTH        = import_class('AuthInterface', 'lense.common.auth.interface')
        self.REQUEST     = import_class('LenseRequestObject', 'lense.common.request', init=False, ensure=pattr('get_request'), [self.PROJECT])
        self.LOG         = import_class('create_project', 'lense.common.log', ensure=pattr('get_logger'), [project])
        self.OBJECTS     = import_class('ObjectsManager', 'lense.common.objects.manager', init=False, ensure=pattr('get_objects'))
        self.USER        = import_class('LenseUser', 'lense.common', init=False, ensure=pattr('get_user'))
        self.CONF        = import_class('parse', 'lense.common.config', init=False, ensure=pattr('get_conf'), [project])
        self.API         = import_class('LenseAPIConstructor', 'lense.common.url', init=False)
        self.URL         = import_class('LenseURLConstructor', 'lense.common', init=False)
        self.MODULE      = import_class('LenseModules', 'lense.common', init=False)
        self.JSON        = import_class('JSONObject', 'lense.common.objects')
        self.FEEDBACK    = import_class('Feedback', 'feedback')
        self.HTTP        = import_class('LenseHTTP', 'lense.common.http', init=False)
    
def init_project(project, name='LENSE'):
    """
    Method for registering a project's common object in the global namespace.
    
    :param project: The project ID to register
    :type  project: str
    """
    if not hasattr(PROJECTS, project):
        raise InvalidProjectID(project)
    
    # Set up the project singletons
    setattr(__builtin__, name, LenseCommon(project))