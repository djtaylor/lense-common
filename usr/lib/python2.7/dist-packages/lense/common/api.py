from lense import import_class
from json import loads as json_loads
from lense.common.exceptions import RequestError

class LenseAPIRequestMapper(object):
    """
    Map the incoming request to an API request handler.
    """ 
    @classmethod
    def run(cls):
        """
        Main method for constructing and returning the handler map.
        """
        
        # Request path and method
        path    = LENSE.REQUEST.path
        method  = LENSE.REQUEST.method
        
        # Get the handler
        handler = LENSE.ensure(LENSE.OBJECTS.HANDLER.get_internal(path=path, method=method),
            isnot = None,
            error = 'Could not find handler for: path={0}, method={1}'.format(path, method),
            debug = 'Retrieved handler object for: path={0}, method={1}'.format(path, method),
            code  = 404)
    
        # Construct the request map object
        return {
            'module':       handler.mod,
            'class':        handler.cls,
            'path':         handler.path,
            'desc':         handler.desc,
            'method':       handler.method,
            'anon':         handler.allow_anon,
            'use_manifest': handler.use_manifest,
            'uuid':         handler.uuid
        }

class LenseAPIConstructor(object):
    """
    Helper class for constructing API classes.
    """
    @staticmethod
    def map_request():
        """
        Run the API request mapper for the current request object.
        """
        return LenseAPIRequestMapper.run()
        
    @staticmethod
    def create_logger():
        """
        Initialize the API logger.
        """
        setattr(LENSE.API, 'LOG', import_class('LenseAPILogger', 'lense.common.logger'))