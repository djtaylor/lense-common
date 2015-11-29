from sys import getsizeof

# Lense Libraries
from lense.common import logger 
from lense.common.utils import truncate
from lense.common.collection import Collection
from lense.common.http import HTTP_POST, HTTP_PUT, HEADER, PATH

class LenseRequestSession(object):
    """
    Helper class for handling session attributes.
    """
    def __init__(self, session):
        self._session = session
        
        # Session ID
        self.id       = getattr(session, 'session_id', None)  
        
    def SET(self, key, value):
        """
        Set a new session value or update an existing one
        """
        self._session[key] = value
        
    def GET(self, key, default=None):
        """
        Retrieve a session value.
        """
        return getattr(self._session, key, default)

class LenseRequestUser(object):
    """
    Helper class for extracting and storing user attributes.
    """
    def __init__(self, request):
        
        # Internal Django request / user object / username / user model
        self._request   = request
        self.object     = request.user
        self.name       = self._getattr('username', header=HEADER.API_USER)
        self.model      = self._getmodel()
 
        # User attributes
        self.group      = self._getattr('group', header=HEADER.API_GROUP, session='active_group')
        self.authorized = self._getattr('is_authenticated', default=False)
        self.admin      = self._getattr('is_admin', default=False, session='is_admin', model=True)
        self.active     = self._getattr('is_active', default=False, model=True)
        self.passwd     = self._getattr('password', default=None, post=True)
    
    def _format_header(self, header):
        """
        Format a header into a Django recognizable string.
        """
        return 'HTTP_{0}'.format(header.upper().replace('-', '_'))
    
    def _getmodel(self):
        """
        Retrieve the user model.
        """
        
        # Import the user object
        from lense.common.objects.user.models import APIUser
        
        # Return the user model
        return None if not self.name else APIUser.objects.filter(username=self.name).values()[0]
    
    def _getattr(self, key, default=None, header=None, session=None, model=False):
        """
        Helper method for retrieving a user attribute.
        """
        
        # Attempt session retrieval
        if session and session in self._request.session:
            return self._request.session.get(session, default)
        
        # Attempt header retrieval
        if header and self._format_header(header) in self._request.META:
            return self._request.META.get(self._format_header(header), default)
        
        # Attempt model retrieval
        if model and isinstance(self.model, dict):
            return self.model.get(key, default)
            
        # Attempt POST variable retrieval
        if post and hasattr(self._request, 'POST'):
            return getattr(self._request.POST, key, default)
            
        # Get attribute from user object
        attr = getattr(self.object, key, default)
        
        # Return the attribute or return value of method
        return attr if not callable(attr) else attr()

class LenseRequestObject(object):
    """
    Extract and construct information from the Django request object.
    """
    def _log_request(self):
        """
        Log incoming requests to the request log.
        """
        LENSE.LOG.info('method={0}, path={1}, client={2}, user={3}, group={4}, key={5}, token={6}, data={7}'.format(
            self.method,
            self.path,
            self.client,
            self.user.name,
            self.user.group,
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
            data_str = getattr(self.django, 'body', '{}')
            
            # Return the JSON object
            return self._json_decode(data_str)
        
        # GET/DELETE requests
        else:
            data = {}
            
            # Store the query string
            query_str = self.django.META['QUERY_STRING']
            
            # If the query string is not empty
            if query_str:
                
                # Process each query string key
                for query_pair in self.django.META['QUERY_STRING'].split('&'):
                    
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
    
    def _get_header_value(self, k, default=None):
        """
        Extract a value from the request headers.
        """
        return self.django.META.get(k, default)
    
    def GET(self, key, default=None):
        """
        Retrieve a key value from GET variables.
        """
        return getattr(self._GET, key, default)
    
    def POST(self, key, default=None):
        """
        Retrieve a key value from POST variables.
        """
        return getattr(self._POST, key, default)
    
    def set(self, request):
        """
        @param request: The incoming Django request object
        @type  project: DjangoRequest
        """
    
        # Store the raw request object and headers
        self.DJANGO       = request
        self.headers      = request.META
        
        # Request method / path / client / host / agent / query string / script / current URI
        self.method       = self._get_header_value('REQUEST_METHOD')
        self.path         = self._get_header_value('PATH_INFO')[1:]
        self.client       = self._get_header_value('REMOTE_ADDR')
        self.host         = self._get_header_value('HTTP_HOST').split(':')[0]
        self.agent        = self._get_header_value('HTTP_USER_AGENT')
        self.query        = self._get_header_value('QUERY_STRING')
        self.script       = self._get_header_value('SCRIPT_NAME')
        self.current      = self._get_header_value('REQUEST_URI')
        
        # Request size / payload
        self.size         = int(getsizeof(getattr(request, 'body', '')))
        self.data         = self._load_data()
    
        # Request user / session
        self.USER         = LenseRequestUser(request)
        self.SESSION      = LenseRequestSession(request.session)
    
        # Anonymous / token request boolean flags
        self.is_anonymous = True if not self.user.name else False
        self.is_token     = True if (self.path == PATH.GET_TOKEN) else False
    
        # API key / token
        self.key          = self._get_key()
        self.token        = self._get_token()
        
        # Method / GET / POST / body data
        self._GET         = Collection(request.GET).get()
        self._POST        = Collection(request.POST).get()
        self.body         = request.body
    
        # Debug logging for each request
        self._log_request()