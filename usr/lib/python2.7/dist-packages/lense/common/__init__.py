__version__ = '0.1.1'

# Python Libraries
import __builtin__
import os
from shutil import rmtree
from subprocess import Popen, PIPE
from sys import path, exit, stderr
from shutil import move as move_file

# Lense Libraries
from lense import import_class
from lense.common.vars import PROJECTS
from lense import MODULE_ROOT, DROPIN_ROOT
from lense.common.exceptions import InvalidProjectID, InitializeError, EnsureError

# Drop-in Python path
path.append(DROPIN_ROOT)

class LenseSetup(object):
    """
    Helper class for setting up commons for handling project requests.
    """
    @classmethod
    def engine(cls, request):
        """
        Setup Lense commons for handling API requests.
        """
        LENSE.REQUEST.set(request)
        LENSE.API.create_logger()
        LENSE.AUTH.ACL.enable()
        cls.socket()

    @classmethod
    def socket(cls):
        """
        Setup the Socket.IO proxy server connection.
        """
        LENSE.SOCKET = import_class('LenseSocketIO', 'lense.common.socket')
        LENSE.SOCKET.set()

    @classmethod
    def portal(cls, request):
        """
        Setup Lense commons for handling portal requests.
        """
        LENSE.REQUEST.set(request)
        LENSE.PORTAL = import_class('PortalInterface', 'lense.portal')

    @classmethod
    def auth(cls):
        """
        Setup Lense authentication backend.
        """
        LENSE.AUTH = import_class('AuthInterface', 'lense.common.auth')

    @classmethod
    def client(cls):
        """
        Setup the Lense client for handling module/CLI level requests.
        """
        LENSE.CLIENT = import_class('ClientInterface', 'lense.client.interface')

class LenseCommon(object):
    """
    Common class for creating project specific instances of common libraries,
    variables, and modules.
    """
    def __init__(self, project):
        
        # Get the project attributes
        self.PROJECT  = import_class('LenseProject', 'lense.common.project', args=[project])
        
        # Generic storage
        self._storage = {}
        
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
        self.REQUEST     = import_class('LenseRequestObject', 'lense.common.request', ensure=pattr('get_request'))
        self.LOG         = import_class('create_project', 'lense.common.logger', args=[project])
        self.OBJECTS     = import_class('LenseAPIObjects', 'lense.common.objects', ensure=pattr('get_objects'))
        self.CONF        = import_class('parse', 'lense.common.config', args=[project])
        self.API         = import_class('LenseAPIConstructor', 'lense.common.api', init=False)
        self.URL         = import_class('LenseURLConstructor', 'lense.common.url', init=False)
        self.MODULE      = import_class('LenseModules', 'lense.common.modules', init=False)
        self.JSON        = import_class('JSONObject', 'lense.common.objects')
        self.FEEDBACK    = import_class('Feedback', 'feedback')
        self.FS          = import_class('LenseFS', 'lense.common.fs', init=False)
        self.HTTP        = import_class('LenseHTTP', 'lense.common.http', init=False)
        self.MAIL        = import_class('LenseAPIEmail', 'lense.common.mailer', init=False)
        self.SETUP       = import_class('LenseSetup', 'lense.common', init=False)
        self.CLIENT      = None
        self.SOCKET      = None
        self.PORTAL      = None
        self.AUTH        = None
        
        # Initialize logs
        self._log_startup()
        
    def retrieve(self, key, default=None):
        """
        Retrieve a key value from generic storage.
        """
        return self._storage.get(key, default)
        
    def store(self, key, value):
        """
        Store a key/value pair in generic storage.
        """
        self._storage[key] = value
        
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
        
    def rmfile(self, file):
        """
        Remove a file/symlink if it exists.
        
        :param file: The target file
        :type  file: str
        """
        if os.path.isfile(file) or os.path.islink(file):
            unlink(file)
        
    def rmdir(self, path):
        """
        Recursively remove a directory.
        
        :param path: The directory to remove
        :type  path: str
        """
        if os.path.isdir(path):
            rmtree(path)
        
    def mvfile(self, src, dst):
        """
        Move a file from one place to another.
        
        :param src: The source file
        :type  src: str
        :param dst: The destination file
        :type  dst: str
        """
        move_file(src, dst)
        
    def mklink(self, target, link):
        """
        Make a symbolic link.
        
        :param target: The target file
        :type  target: str
        :param   link: The target link
        :type    link: str
        """
        os.symlink(target, link)
        
    def mkdir(self, dir_path):
        """
        Make a directory and return the path name.
        
        :rtype: str
        """
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        return dir_path
        
    def shell_exec(self, cmd, show_stdout=True):
        """
        Run an arbitrary system command.
        
        :param cmd: The command list to run
        :type  cmd: list
        """
        
        # If showing stdout
        if show_stdout:
            proc = Popen(cmd, stderr=PIPE)
            err = proc.communicate()
            
        # If supressing stdout
        else:
            proc = Popen(cmd, stderr=PIPE, stdout=PIPE)
            out, err = proc.communicate()

        # Return code, stderr
        return proc.returncode, err
        
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
    
    # Cannot reinitialize project
    if hasattr(__builtin__, name):
        raise InitializeError(project, 'Already initialized: {0}'.format(repr(getattr(__builtin__, name))))
    
    # Set up the project singletons
    setattr(__builtin__, name, LenseCommon(project))