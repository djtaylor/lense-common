__version__ = '0.1.1'

# Python Libraries
import __builtin__
from sys import path, exit, stderr

# Lense Libraries
from lense import import_class
from lense.common.vars import PROJECTS
from lense import MODULE_ROOT, DROPIN_ROOT
from lense.common.exceptions import InvalidProjectID, EnsureError

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
        self.LOG         = import_class('create_project', 'lense.common.logger', args=[project])
        self.OBJECTS     = import_class('LenseAPIObjects', 'lense.common.objects', ensure=pattr('get_objects'))
        self.CONF        = import_class('parse', 'lense.common.config', args=[project])
        self.API         = import_class('LenseAPIConstructor', 'lense.common.api', init=False)
        self.URL         = import_class('LenseURLConstructor', 'lense.common.url', init=False)
        self.MODULE      = import_class('LenseModules', 'lense.common.modules', init=False)
        self.JSON        = import_class('JSONObject', 'lense.common.objects')
        self.FEEDBACK    = import_class('Feedback', 'feedback')
        self.HTTP        = import_class('LenseHTTP', 'lense.common.http', init=False)
        self.MAIL        = import_class('LenseAPIEmail', 'lense.common.mailer', init=False)
        self.SOCKET      = None
        
        # Initialize logs
        self._log_startup()
        
    def _log_startup(self):
        """
        Start the logs for this project run.
        """
        self.LOG.info('Starting project: lense-{0}'.format(self.PROJECT.name.lower()))
        
        # Log the configuration
        for s,a in self.CONF.__dict__.iteritems():
            for k,v in a.__dict__.iteritems():
                self.LOG.debug('[config] -> {0}.{1} = {2}'.format(s,k,v))
        
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
        
    def ensure(self, result, **kwargs):
        """
        Ensure a result is equal to 'value' or is not equal to 'isnot'. Raise a RequestError otherwise.
        
        :param result: The result to check
        :type  result: mixed
        :param  value: The value to ensure (equal to)
        :type   value: mixed
        :param  isnot: The value to ensure (not equal to)
        :type   isnot: mixed
        :param  error: The error message to raise
        :type   error: str
        :param   code: The HTTP status code to return if error
        :type    code: int
        :param   call: Call the result object as a method
        :type    call: mixed
        :param   args: Arguments to pass to the object method
        :type    args: list
        :param kwargs: Keyword arguments to pass to the object method
        :type  kwargs: dict
        :param    log: Log a success message
        :type     log: str
        :param  debug: Log a debug message
        :type   debug: str
        :param    exc: The type of exception to raise
        :type     exc: object
        :rtype: result
        """
        
        # Code / error / call / log / debug
        code  = kwargs.get('code', 400)
        error = kwargs.get('error', 'An unknown request error has occurred')
        call  = kwargs.get('call', False)
        log   = kwargs.get('log', None)
        debug = kwargs.get('debug', None)
        exc   = kwargs.get('exc', EnsureError)
        
        # Cannot specify both value/isnot at the same time
        if ('value'in kwargs) and ('isnot' in kwargs):
            raise Exception('Cannot supply both "value" and "isnot" arguments at the same time')
        
        # Equal to / not equal to
        value = kwargs.get('value', None)
        isnot = kwargs.get('isnot', None)
        
        # If calling the result object as a method
        if call:
            
            # Args / kwargs
            call_args = kwargs.get('args', [])
            call_kwargs = kwargs.get('kwargs', {})
            
            # Method must be callable
            if not callable(result):
                raise exc('Cannot ensure <{0}>, object not callable'.format(repr(result)))
            
            # Attempt to run the method
            try:
                result = result(*call_args, **call_kwargs)
            except Exception as e:
                raise exc('Failed to call <{0}>: {1}'.format(repr(result, str(e))), 500)
        
        # Negative check (not equal to)
        if 'isnot' in kwargs:
            if result == isnot:
                raise exc(error, code)
        
        # Positive check (equal to)
        if 'value' in kwargs:
            if result != value:
                raise exc(error, code)
        
        # Log info/debug
        if log:
            LENSE.LOG.info(log)   
        if debug:
            LENSE.LOG.debug(debug)
        
        # Return the result
        return result
        
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