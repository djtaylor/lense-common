import time
import logging
import logging.handlers
from os import makedirs
from os.path import isdir, dirname

# Lense Libraries
from lense.common.project import LenseProject

class LogFormat(logging.Formatter):
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
        s  = time.strftime(datefmt, ct)
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
        logger = logging.getLogger(name)
        
        # Don't create duplicate handlers
        if not len(logger.handlers):
            logger.setLevel(logging.INFO)
            
            # Set the file handler
            lfh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10*1024*1024, backupCount=5)
            logger.addHandler(lfh)
            
            # Set the format
            lfm = LogFormat(fmt='%(asctime)s %(name)s - %(levelname)s: %(message)s', datefmt='%d-%m-%Y %I:%M:%S')
            lfh.setFormatter(lfm)
        return logging.getLogger(name)
    
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