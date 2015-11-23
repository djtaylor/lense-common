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
        self.name = 'lense.{0}'.format(project)
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
        self.name      = project
        
        # Get the project attributes
        self._attrs    = getattr(PROJECTS, project, None)
        
        # Configuration and log files
        self.log       = _LenseProjectLog(project)
        self.conf      = getattr(self._attrs, 'CONF', None)
        
        # Project templates
        self.TEMPLATES = getattr(TEMPLATES, project, None)
        
        # Use a Django request object or not
        self.use_request = getattr(self._attrs, 'REQUEST', False)
        
        # Use the objects manager or not
        self.use_objects = getattr(self._attrs, 'OBJECTS', False)