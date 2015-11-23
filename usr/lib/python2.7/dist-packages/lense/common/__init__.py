__version__ = '0.1.1'

# Python Libraries
import re
import json
from feedback import Feedback
from sys import getsizeof, path
from importlib import import_module

# Lense Libraries
from lense.common import config
from lense.common import logger
from lense.common.http import HEADER
from lense import MODULE_ROOT, DROPIN_ROOT
from lense.common.objects import JSONObject
from lense.common.utils import valid, invalid
from lense.common.collection import Collection
from lense.common.projects import LenseProjects
from lense.common.vars import PROJECTS, TEMPLATES
from lense.common.request import LenseRequestObject
from lense.common.exceptions import InvalidProjectID
from lense.common.objects.manager import ObjectsManager

# Drop-in Python path
path.append(DROPIN_ROOT)

class LenseModules(object):
    """
    Module helper class.
    """
    def __init__(self):
        
        # Built-in/drop-in module roots
        self.ROOT    = MODULE_ROOT
        self.DROPIN  = self._get_dropin_modules()
        self.BUILTIN = self._get_builin_modules()
    
    def _dropin_path_map(self, rel):
        """
        Map a relative module path to the drop-in root.
        """
        return '{0}/lense_d/{1}'.format(DROPIN_ROOT, rel)
    
    def _builtin_path_map(self, rel):
        """
        Map a relative path to the built-in root.
        """
        return '{0}/{1}'.format(MODULE_ROOT, rel)
    
    def _get_dropin_modules(self):
        """
        Drop-in module attributes.
        """
        return Collection({
            'CLIENT': [self._dropin_path_map('client/modules'), 'lense_d.client.modules']
        }).get()
    
    def _get_builtin_modules(self):
        """
        Built-in module attributes.
        """
        return Collection({
            'CLIENT': [self._builtin_path_map('client/modules'), 'lense.client.modules']
        }).get()
    
    def NAME(self, file):
        """
        Extract a module name from a file path.
        """
        return re.compile(r'^([^\.]*)\..*$').sub(r'\g<1>', file)
    
    def IMPORT(self, module):
        """
        Import a built-in or drop-in module.
        """
        return import_module(module)

class LenseCommon(object):
    """
    Common class for creating project specific instances of common libraries,
    variables, and modules.
    """
    def __init__(self, project):
        
        # Get the project attributes
        self.PROJECT     = LenseProject(project)
        
        """
        Project Objects
        
        COLLECTION: Immutable collection generator
        REQUEST:    Generate a request object or not
        LOG:        Create the log handler if needed
        OBJECTS:    Create the object manager if needed
        MODULE:     The module helper
        JSON:       JSON object manager
        INVALID:    Error relay
        VALID:      Success relay 
        FEEDBACK:   CLI feedback handler
        """
        self.COLLECTION  = Collection
        self.REQUEST     = None if not self.PROJECT.use_request else LenseRequestObject(self.PROJECT)
        self.LOG         = None if not self.PROJECT.log.file else logger.create_project(project)
        self.OBJECTS     = None if not self.PROJECT.use_objects else ObjectsManager()
        self.CONF        = None if not self.PROJECT.conf else config.parse(project)
        self.MODULE      = LenseModules()
        self.JSON        = JSONObject()
        self.INVALID     = invalid
        self.VALID       = valid
        self.FEEDBACK    = Feedback()