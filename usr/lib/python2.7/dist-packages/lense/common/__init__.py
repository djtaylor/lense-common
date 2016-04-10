__version__ = '0.1.1'

# Python Libraries
import __builtin__
import os
import re
from shutil import rmtree
from threading import Thread
from subprocess import Popen, PIPE
from sys import path, exit, stderr
from shutil import move as move_file

# Lense Libraries
from lense import import_class
from lense.common.vars import PROJECTS
from lense.common.base import LenseBase
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

class LenseCommon(LenseBase):
    """
    Common class for creating project specific instances of common libraries,
    variables, and modules.
    """
    def __init__(self, project):
        super(LenseCommon, self).__init__(project)
        
        # Get the project attributes
        self.PROJECT  = import_class('LenseProject', 'lense.common.project', args=[project])
        
        # Get project attribute
        def pattr(a):
            return getattr(self.PROJECT, a, False)
        
        """
        Project Objects
        """     
        
        self.REQUEST     = import_class('LenseRequestObject', 'lense.common.request', ensure=pattr('get_request'))
        self.OBJECTS     = import_class('LenseAPIObjects', 'lense.common.objects', ensure=pattr('get_objects'))
        self.API         = import_class('LenseAPIConstructor', 'lense.common.api', init=False)
        self.URL         = import_class('LenseURLConstructor', 'lense.common.url', init=False)
        self.MODULE      = import_class('LenseModules', 'lense.common.modules', init=False)
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
    
    # Set up the project commons
    setattr(__builtin__, name, LenseCommon(project))