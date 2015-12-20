from lense.common.vars import PROJECTS, TEMPLATES
from lense.common.exceptions import InvalidProjectID

class _LenseProjectLog(object):
    """
    Private class for mapping project log attributes.
    """
    def __init__(self, project):
        """
        @param project: The target project
        @type  project: str
        """
        self.name = 'lense.{0}'.format(project.lower())
        self.file = getattr(getattr(PROJECTS, project), 'LOG', None)

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
        
        # Get the project attributes
        self._attrs      = getattr(PROJECTS, project, None)
        
        # Configuration and log files
        self.LOG         = _LenseProjectLog(project)
        self.conf        = getattr(self._attrs, 'CONF', None)
        
        # Project templates
        self.TEMPLATES   = getattr(TEMPLATES, project, None)
        
        # Get request / objects / logger / user / configuration / authentication
        self.get_request = getattr(self._attrs, 'REQUEST', False)
        self.get_logger  = getattr(self._attrs, 'LOG', False)
        self.get_objects = getattr(self._attrs, 'OBJECTS', False)
        self.get_conf    = getattr(self._attrs, 'CONF', False)
        self.get_auth    = getattr(self._attrs, 'AUTH', False)