__version__ = '0.1.1'

# Python Libraries
import __builtin__
from sys import path, exit, stderr

# Lense Libraries
from lense import import_class
from lense.common.vars import PROJECTS
from lense import MODULE_ROOT, DROPIN_ROOT
from lense.common.exceptions import InvalidProjectID

# Drop-in Python path
path.append(DROPIN_ROOT)

class LenseCommon(object):
    """
    Common class for creating project specific instances of common libraries,
    variables, and modules.
    """
    def __init__(self, project):
        
        # Get the project attributes
        self.PROJECT = import_class('LenseProject', 'lense.common.project', args=[project])
        
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
        SOCKET:     SocketIO handler
        """
        self.COLLECTION  = import_class('Collection', 'lense.common.collection', init=False)
        self.AUTH        = import_class('AuthInterface', 'lense.common.auth', ensure=pattr('get_auth'))
        self.REQUEST     = import_class('LenseRequestObject', 'lense.common.request', ensure=pattr('get_request'))
        self.LOG         = import_class('create_project', 'lense.common.logger', ensure=pattr('get_logger'), args=[project])
        self.OBJECTS     = import_class('LenseAPIObjects', 'lense.common.objects', init=False, ensure=pattr('get_objects'))
        self.USER        = import_class('LenseUser', 'lense.common.user', ensure=pattr('get_user'))
        self.GROUP       = import_class('LenseGroup', 'lense.common.group', ensure=pattr('get_user'))
        self.CONF        = import_class('parse', 'lense.common.config', ensure=pattr('get_conf'), args=[project])
        self.API         = import_class('LenseAPIConstructor', 'lense.common.api', init=False)
        self.URL         = import_class('LenseURLConstructor', 'lense.common.url', init=False)
        self.MODULE      = import_class('LenseModules', 'lense.common.modules', init=False)
        self.JSON        = import_class('JSONObject', 'lense.common.objects')
        self.FEEDBACK    = import_class('Feedback', 'feedback')
        self.HTTP        = import_class('LenseHTTP', 'lense.common.http', init=False)
        self.MAIL        = import_class('LenseAPIEmail', 'lense.common.mailer', init=False)
        self.SOCKET      = None
        
    def get_request(self):
        """
        Initialize the request object.
        """
        self.REQUEST = import_class('LenseRequestObject', 'lense.common.request')
        return self.REQUEST
        
    def connect_socket(self):
        """
        Initialize the SocketIO connection.
        """
        self.SOCKET = import_class('LenseSocketIO', 'lense.common.socket')
        return self.SOCKET
        
    def die(self, msg, code=1, pre=None, post=None):
        """
        Print to stderr and immediately exit
        
        :param  msg: The message to render
        :type   msg: str
        :param code: The exit code
        :type  code: int
        :param  pre: Pre-message method
        :type   pre: method
        :param post: Post-message method
        :type  post: method 
        """
        if callable(pre): pre()
        
        # Write the error message to stderr
        stderr.write('{0}\n'.format(msg) if not isinstance(msg, list) else '\n'.join([l for l in msg]))
        if callable(post): post()
        
        # Attempt to log
        if LENSE and hasattr(LENSE, 'LOG'):
            LENSE.LOG.error(msg)
        exit(code)
    
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