from lense import import_class
from json import loads as json_loads
from lense.common.utils import valid, invalid

class LenseAPIRequestMapper(object):
    """
    Map the incoming request to an API request handler.
    """ 
    @staticmethod
    def _merge_socket(j):
        """
        Merge request parameters for web socket request. Used for handling connections
        being passed along by the Socket.IO API proxy.
        
        :param j: The JSON object to map
        :type  j: dict
        """
        
        # Load the socket request validator map
        sv = json_loads(open('{0}/api/base/socket.json'.format(LENSE.PROJECT.TEMPLATES), 'r').read())
        
        # Make sure the '_children' key exists
        if not '_children' in j['root']:
            j['root']['_children'] = {}
        
        # Merge the socket parameters map
        j['root']['_children']['socket'] = sv
        j['root']['_optional'].append('socket')
        
        # Return the mapped object
        return j
        
    @staticmethod
    def run(self):
        """
        Main method for constructing and returning the handler map.
        
        @return valid|invalid
        """
        handler = LENSE.OBJECTS.get_handler()
        
        # Request path and method
        path    = LENSE.REQUEST.path
        method  = LENSE.REQUEST.method
        
        # Handler does not exist
        if not handler:
            return invalid(LENSE.HTTP.error(error='Could not find handler for: path={0}, method={1}'.format(path, method)))
        
        # Load the request map
        rmap = {'root': json_loads(handler.rmap)}
        
        # Merge the web socket request validator
        rmap = LenseAPIRequestMapper._merge_socket(rmap)
    
        # Construct the request map object
        return {
            'module': handler.mod,
            'class':  handler.cls,
            'path':   handler.path,
            'desc':   handler.desc,
            'method': handler.method,
            'anon':   handler.allow_anon,
            'json':   rmap
        }
    
        # Return the handler module path
        return valid(map)

class LenseAPIConstructor(object):
    """
    Helper class for constructing API classes.
    """
    @staticmethod
    def BASE(*args, **kwargs):
        """
        Wrapper method for returning an instance of APIBase.
        """
        return import_class('APIBase', 'lense.engine.api.base', args=args, kwargs=kwargs).construct()
    
    @staticmethod
    def BARE(*args, **kwargs):
        """
        Wrapper method for returning an instance of APIBare.
        """
        return import_class('APIBare', 'lense.engine.api.bare', args=args, kwargs=kwargs)
    
    @staticmethod
    def map_request():
        """
        Run the API request mapper for the current request object.
        """
        return LenseAPIRequestMapper.run()
        