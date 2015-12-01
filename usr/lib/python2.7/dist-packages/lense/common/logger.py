from os import makedirs
from time import strftime
from os.path import isdir, dirname
from json import dumps as json_dumps
from logging import handlers, INFO, getLogger, Formatter

# Django Libraries
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

# Lense Libraries
from lense import set_arg
from lense.common.project import LenseProject
from lense.common.http import MIME_TYPE, JSONError, JSONException

class LenseAPILogger(object):
    """
    APILogger
    
    Common logger class used to handle logging messages and returning HTTP responses.
    """
    def __init__(self):
        """
        :param client: The client IP address
        :type  client: str
        """
        self.msg    = None
        self.client = LENSE.REQUEST.client

    def _reset_client(self, retval=None):
        """
        Reset the API client IP address.
        """
        self.client = LENSE.REQUEST.client
        return retval

    def set_client(self, client):
        """
        Override the default client IP address.
        """
        self.client = client
        return self

    def _websock_response(self, status, data={}):
        """
        Construct and return a JSON web socket response for the Socket.IO proxy server.
        
        :param status: Boolean string
        :type  status: str
        :param data:   Any response data in addition to the body message
        :type  data:   dict
        """
        return json_dumps({
            'room':     LENSE.SOCKET.params.get('room', None),
            'msg':      self.msg,
            'path':     LENSE.REQUEST.path,
            'callback': LENSE.SOCKET.params.get('callback', False),
            'status':   status,
            '_data':    data
        }, cls=DjangoJSONEncoder)

    def _api_response(self, ok=False, data={}):
        """
        Construct the API response body to send back to clients. Constructs the websocket data
        to be interpreted by the Socket.IO proxy server if relaying back to a web client.
        
        :param ok:   Has the request been successfull or not
        :type  ok:   bool
        :param data: Any data to return in the SocketIO response
        :type  data: dict
        """
        
        # Status flag
        status = 'true' if ok else 'false'
        
        # Web socket responses
        if LENSE.SOCKET.params:
            return self._websock_response(status, data)
            
        # Any paths that don't supply web socket responses    
        else:
            if isinstance(self.msg, (dict, list)):
                return json_dumps(self.msg, cls=DjangoJSONEncoder)
            return self.msg

    def info(self, msg):
        """
        Handle the logging of information messages.
        
        :param msg:  The message to log/return to the client
        :type  msg:  str
        """
        self.msg = msg
        LENSE.LOG.info('client({0}): {1}'.format(self.client, msg))
        return self._reset_client(msg)
        
    def debug(self, msg):
        """
        Handle the logging of debug messages.
        
        :param msg:  The message to log/return to the client
        :type  msg:  str
        """
        LENSE.LOG.debug('client({0}): {1}'.format(self.client, msg))
        return self._reset_client(msg)
        
    def success(self, msg='API request was successfull', data={}):
        """
        Handle the logging of success messages. Returns an HTTP response object that can be
        sent by the API request handler back to the client.
        
        :param msg:  The message to log/return to the client
        :type  msg:  str
        :param data: Any additional data to return to a web client via SocketIO
        :type  data: dict
        """
        self.msg = msg
        LENSE.LOG.info('client({}): {}'.format(self.client, msg))
        self._reset_client(HttpResponse(self._api_response(True, data), MIME_TYPE.APPLICATION.JSON, status=200))
    
    def exception(self, msg=None, code=None, data={}):
        """
        Handle the logging of exception messages. Returns an HTTP response object that can be
        sent by the API request handler back to the client.
        
        :param msg:  The message to log/return to the client
        :type  msg:  str
        :param code: The HTTP status code
        :type  code: int
        :param data: Any additional data to return to a web client via SocketIO
        :type  data: dict
        """
        self.msg = 'An exception occured when processing your API request' if not msg else msg
        LENSE.LOG.exception('client({0}): {1}'.format(self.client, self.msg))
    
        # If returning a response to a client
        if code and isinstance(code, int):
            return self._reset_client(JSONException(error=self._api_response(False, data)).response())
        return self._reset_client(self.msg)
    
    def error(self, msg=None, code=None, data={}):
        """
        Handle the logging of error messages. Returns an HTTP response object that can be
        sent by the API request handler back to the client.
        
        :param msg:  The message to log/return to the client
        :type  msg:  str
        :param code: The HTTP status code
        :type  code: int
        :param data: Any additional data to return to a web client via SocketIO
        :type  data: dict
        """
        self.msg = 'An unknown error occured when processing your API request' if not msg else msg
        LENSE.LOG.error('client({0}): {1}'.format(self.client, self.msg))
        
        # If returning a response to a client
        if code and isinstance(code, int):
            return self._reset_client(JSONError(error=self._api_response(False, data), status=code).response())
        return self._reset_client(self.msg)

class LogFormat(Formatter):
    """
    Custom log format object to use with the Python logging module. Used
    to log the message and return the message string for further use.
    """
    def formatTime(self, record, datefmt):
        """
        Format the record to use a datetime prefix.
        
        :param record: The log message
        :type record: str
        :param datefmt: The timestamp format
        :type datefmt: str
        :rtype: str
        """
        ct = self.converter(record.created)
        s  = strftime(datefmt, ct)
        return s

class Logger:
    """
    API logging class. Static constructor is called by the factory method 'create'.
    The log formatter returns the log message as a string value. Used mainly to log
    a message and return the value so it can be passed into an HTTP response.
    """
    @ staticmethod
    def construct(name, log_file):
        """
        Construct the logging object. If the log handle already exists don't create
        anything so we don't get duplicated log messages.
        
        :param name: The class or module name to use in the log message
        :type name: str
        :param log_file: Where to write log messages to
        :type log_file: str
        :rtype: logger
        """
        
        # Make sure the log directory exists
        log_dir = dirname(log_file)
        if not isdir(log_dir):
            makedirs(log_dir, 0755)
        
        # Set the logger module name
        logger = getLogger(name)
        
        # Don't create duplicate handlers
        if not len(logger.handlers):
            logger.setLevel(INFO)
            
            # Set the file handler
            lfh = handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10*1024*1024, backupCount=5)
            logger.addHandler(lfh)
            
            # Set the format
            lfm = LogFormat(fmt='%(asctime)s %(name)s - %(levelname)s: %(message)s', datefmt='%d-%m-%Y %I:%M:%S')
            lfh.setFormatter(lfm)
        return getLogger(name)
    
def create_project(project):
    """
    Wrapper method for creating a project logger instance.
    """
    PROJECT = LenseProject(project)
    
    # Return a logger object
    return create(PROJECT.LOG.name, PROJECT.LOG.file)
    
def create(name=False, log_file=None):
    """
    Factory method used to construct and return a Python logging object. Must supply
    a module prefix as well as a log file.
    
    Constructing a logging object::
    
        # Import the logging module
        import lense.common.logger as logger
        
        # Create a new log object
        LOG = logger.create('some.module.name', '/path/to/file.log')
    
        # Logging messages
        LOG.info('Some message to log')
        LOG.error('Something bad happened')
        LOG.exception('Abort! Abort!')
        
        # Capturing the log message
        msg = LOG.info('This will be stored in the "msg" variable')
    
    :param name: The module prefix
    :type name: str
    :param log_file: The log file destination
    :type log_file: str
    :rtype: Logger
    """
    if name and log_file:
        return Logger.construct(name, log_file)
    raise Exception('Logger factory method must have a module name and log file as arguments')