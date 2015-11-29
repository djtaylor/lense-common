__version__ = '0.1.1'

# Python Libraries
import __builtin__
from sys import path

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
        self.PROJECT     = import_class('LenseProject', 'lense.common.project', args=[project])
        
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
        self.AUTH        = import_class('AuthInterface', 'lense.common.auth')
        self.REQUEST     = import_class('LenseRequestObject', 'lense.common.request', init=False, ensure=pattr('get_request'), args=[self.PROJECT])
        self.LOG         = import_class('create_project', 'lense.common.logger', ensure=pattr('get_logger'), args=[project])
        self.OBJECTS     = import_class('ObjectsManager', 'lense.common.objects.manager', init=False, ensure=pattr('get_objects'))
        self.USER        = import_class('LenseUser', 'lense.common', init=False, ensure=pattr('get_user'))
        self.CONF        = import_class('parse', 'lense.common.config', init=False, ensure=pattr('get_conf'), args=[project])
        self.API         = import_class('LenseAPIConstructor', 'lense.common.api', init=False)
        self.URL         = import_class('LenseURLConstructor', 'lense.common.url', init=False)
        self.MODULE      = import_class('LenseModules', 'lense.common.modules', init=False)
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