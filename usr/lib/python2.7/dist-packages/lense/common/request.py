from lense.common import logger 
from lense.common.utils import truncate
from lense.common.collection import Collection
from lense.common.http import HTTP_POST, HTTP_PUT, HEADER

class LenseRequestObject(object):
    """
    Extract and construct information from the Django request object.
    """
    def __init__(self, project):
        """
        @param project: The target project
        @type  project: str
        """
        self._project = project
    
        # Internal request logger
        self._log = self._get_request_logger()
    
    def _log_request(self):
        """
        Log incoming requests to the request log.
        """
        self._log.info('method={0}, path={1}, client={2}, user={3}, group={4}, key={5}, token={6}, data={7}'.format(
            self.method,
            self.path,
            self.client,
            self.user,
            self.group,
            self.key,
            self.token,
            truncate(str(self.data))
        ))
    
    def _load_data(self):
        """
        Load request data depending on the method. For POST requests, load the request
        body, for GET requests, load the query string.
        """
    
        # PUT/POST requests
        if self.method in [HTTP_POST, HTTP_PUT]:
            
            # Load the data string and strip special characters
            data_str = getattr(self.RAW, 'body', '{}')
            
            # Return the JSON object
            return self._json_decode(data_str)
        
        # GET/DELETE requests
        else:
            data = {}
            
            # Store the query string
            query_str = self.RAW.META['QUERY_STRING']
            
            # If the query string is not empty
            if query_str:
                
                # Process each query string key
                for query_pair in self.RAW.META['QUERY_STRING'].split('&'):
                    
                    # If processing a key/value pair
                    if '=' in query_pair:
                        query_set = query_pair.split('=')
                        
                        # Return JSON if possible
                        try:
                            data[query_set[0]] = json.loads(query_set[1])
                            
                        # Non-JSON parseable value
                        except:
                            
                            # Integer value
                            try:
                                data[query_set[0]] = int(query_set[1])
                            
                            # String value
                            except:
                                data[query_set[0]] = query_set[1]
                        
                    # If processing a key flag
                    else:
                        data[query_pair] = True
                        
            # Return the request data
            return data
    
    def _json_decode(self, json_str):
        """
        Hack/helper method for properly decoding JSON strings.
        """
        
        # If the string is empty
        if not json_str:
            return {}
        
        # If already an object
        if isinstance(json_str, dict):
            return json_str
        
        # Decode the data
        json_data = json.loads(json_str)
        if not isinstance(json_data, dict):
            
            # If still needs further decoding
            return self._json_decode(json_data)
        return json_data
    
    def _get_request_logger(self):
        """
        Construct and return the internal request logger.
        """
        _name  = '{0}.request'.format(self._project.log.name)
        _file  = self._project.log.file.replace(self._project.name, '{0}.request'.format(self._project.name))

        # Construct and return the logger
        self._log = logger.create(_name, _file)
    
    def _get_group(self):
        """
        Retrieve the group from either the request headers or request object
        depending on the project.
        """
    
        # Engine API user
        if self._project.name == 'ENGINE':
           return self.headers.get('HTTP_{0}'.format(HEADER.API_GROUP.upper().replace('-', '_')))
           
        # Portal user
        if self._project.name == 'PORTAL': 
            return None if not self.request.user.is_authenticated() else self.request.session['active_group']
    
    def _get_user(self):
        """
        Retrieve the user from either the request headers or request object
        depending on the project.
        """
        
        # Engine API user
        if self._project.name == 'ENGINE':
           return self.headers.get('HTTP_{0}'.format(HEADER.API_USER.upper().replace('-', '_')))
           
        # Portal user
        if self._project.name == 'PORTAL': 
            return None if not hasattr(self.request, 'user') else self.request.user.username
    
    def _get_key(self):
        """
        Attempt to retrieve an API key from headers.
        """
        return self.headers.get('HTTP_{0}'.format(HEADER.API_KEY.upper().replace('-', '_')), '')
    
    def _get_token(self):
        """
        Attempt to retrieve an API token from headers.
        """
        return self.headers.get('HTTP_{0}'.format(HEADER.API_TOKEN.upper().replace('-', '_')), '')
    
    def _get_session(self):
        """
        Attempt to retrieve a session key from the request object.
        """
        return None if not hasattr(self.request, 'session') else self.request.session.session_key
    
    def _get_admin(self):
        """
        Attempt to determine if the request user has administrative privileges.
        """
        if self._project.name == 'PORTAL':
            return False if not self.request.user.is_authenticated() else self.request.session['is_admin']
    
    def _get_header_value(self, k, default=None):
        """
        Extract a value from the request headers.
        """
        return self.request.META.get(k, default)
    
    def SET(self, request):
        """
        @param request: The incoming Django request object
        @type  project: DjangoRequest
        """
    
        # Store the raw request object and headers
        self.RAW         = request
        self.headers     = request.META
        
        # Request method / path / client / host / agent / query string / script / current URI
        self.method      = self._get_header_value('REQUEST_METHOD')
        self.path        = self._get_header_value('PATH_INFO')[1:]
        self.client      = self._get_header_value('REMOTE_ADDR')
        self.host        = self._get_header_value('HTTP_HOST').split(':')[0]
        self.agent       = self._get_header_value('HTTP_USER_AGENT')
        self.query       = self._get_header_value('QUERY_STRING')
        self.script      = self._get_header_value('SCRIPT_NAME')
        self.current     = self._get_header_value('REQUEST_URI')
        
        # Request size / payload
        self.size        = int(getsizeof(getattr(request, 'body', '')))
        self.data        = self._load_data()
    
        # User / group / key / token / session / is_admin
        self.user        = self._get_user()
        self.group       = self._get_group()
        self.key         = self._get_key()
        self.token       = self._get_token()
        self.session     = self._get_session()
        self.is_admin    = self._get_admin()
        
        
        # Method / GET / POST / body data
        self.GET         = Collection(request.GET).get()
        self.POST        = Collection(request.POST).get()
        self.body        = request.body
    
        # Debug logging for each request
        self._log_request()