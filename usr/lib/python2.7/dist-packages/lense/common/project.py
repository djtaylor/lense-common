import syslog

# Lense Libraries
from lense import import_class
from lense.common.vars import PROJECTS, TEMPLATES
from lense.common.exceptions import InvalidProjectID

class _LenseProjectLog(object):
    """
    Private class for mapping project log attributes.
    """
    def __init__(self, project, conf=None):
        """
        @param project: The target project
        @type  project: str
        """
        self._project = project
        self._conf    = self._get_config(conf)
        
        # Log name / file / level
        self.name     = 'lense.{0}'.format(project.lower())
        self.file     = getattr(self._conf, 'log', None)
        self.level    = getattr(self._conf, 'log_level', 'INFO')

    def _get_config(self, conf):
        """
        Retrieve a configuration for the project log attributes class.
        """
        if not conf:
            return conf
        
        # Load the project configuration
        conf = import_class('parse', 'lense.common.config', args=[self._project])
        return getattr(conf, self._project.lower(), None)

class LenseProject(object):
    """
    Class for storing project attributes.
    """
    def __init__(self, project):
        """
        @param project: The target project
        @type  project: str
        """
        if not hasattr(PROJECTS, project):
            raise InvalidProjectID(project)
        
        # Project name
        self.name        = project
        
        # Project attributers / configuration file
        self._attrs      = getattr(PROJECTS, project, None)
        self.conf        = getattr(self._attrs, 'CONF', None)
        
        # Log attributes
        self.LOG         = _LenseProjectLog(project, self.conf)
        
        # Project templates
        self.TEMPLATES   = getattr(TEMPLATES, project, None)
        
        # Get request / objects / user / configuration / authentication
        self.get_request = getattr(self._attrs, 'REQUEST', False)
        self.get_objects = getattr(self._attrs, 'OBJECTS', False)
        self.get_conf    = getattr(self._attrs, 'CONF', False)
        self.get_auth    = getattr(self._attrs, 'AUTH', False)