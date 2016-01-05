from lense import import_class
from json import loads as json_loads
from lense.common.utils import valid, invalid
from lense.common.exceptions import RequestError

class LenseAPIRequestMapper(object):
    """
    Map the incoming request to an API request handler.
    """ 
    @classmethod
    def _merge_socket(cls, rmap):
        """
        Merge request parameters for web socket request. Used for handling connections
        being passed along by the Socket.IO API proxy.
        
        :param rmap: The request handler mapper JSON object
        :type  rmap: dict
        """
        sock_template = '{0}/api/base/socket.json'.format(LENSE.PROJECT.TEMPLATES)
        sock_map = json_loads(open(sock_template, 'r').read())
        
        # Make sure the '_children' key exists
        if not '_children' in rmap['root']:
            rmap['root']['_children'] = {}
        
        # Merge the socket parameters map
        rmap['root']['_children']['socket'] = sock_map
        rmap['root']['_optional'].append('socket')
        return rmap
        
    @classmethod
    def run(cls):
        """
        Main method for constructing and returning the handler map.
        
        @return valid|invalid
        """
        
        # Request path and method
        path    = LENSE.REQUEST.path
        method  = LENSE.REQUEST.method
        
        # Get the handler
        handler = LENSE.ensure(LENSE.OBJECTS.HANDLER.get(path=path, method=method),
            isnot = None,
            error = 'Could not find handler for: path={0}, method={1}'.format(path, method),
            debug = 'Retrieved handler object for: path={0}, method={1}'.format(path, method),
            code  = 404)
        
        # Load the request map
        rmap = {'root': json_loads(handler.rmap)}
        
        # Merge the web socket request validator
        rmap = cls._merge_socket(rmap)
    
        # Construct the request map object
        return {
            'module': handler.mod,
            'class':  handler.cls,
            'path':   handler.path,
            'desc':   handler.desc,
            'method': handler.method,
            'anon':   handler.allow_anon,
            'rmap':   rmap
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