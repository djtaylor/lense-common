import json
from re import compile
from sys import getsizeof

# Django Libraries
from django.test.client import RequestFactory

# Lense Libraries
from lense import import_class
from lense.common import logger 
from lense.common.utils import truncate
from lense.common.collection import Collection
from lense.common.exceptions import RequestError
from lense.common.http import HTTP_GET, HTTP_POST, HTTP_PUT, HEADER, PATH
from django.template.defaultfilters import default

class LenseWSGIRequest(object):
    """
    Helper class for constructing a dummy WSGI request object.
    """ 
    @staticmethod
    def get(path='token', data=None, method=HTTP_GET):
        """
        Factory method for constructing a RequestFactory.
        
        :param path:   The API request path
        :type  path:   str
        :param data:   The API request data
        :type  data:   dict
        :param method: The API request method
        :param type:   str
        """
        
        # Generate a Django request object
        factory = RequestFactory(**{
            'REQUEST_METHOD': method,
            'SERVER_NAME':    'localhost',
            'PATH_INFO':      '/{}'.format(path),
            'REQUEST_URI':    '/api/{}'.format(path),
            'SCRIPT_NAME':    '/api',
            'SERVER_PORT':    '10550', 
            'CONTENT_TYPE':   'application/json',
            'REMOTE_ADDR':    '127.0.0.1',
            'REMOTE_HOST':    'localhost',
            'HTTP_HOST':      '127.0.0.1:80',
            'QUERY_STRING':   ''
        })
        
        # Get the request handler
        r_handler = getattr(factory, method.lower())
        
        # Request requires a query string
        if method == HTTP_GET:
            query_str = '?{0}'.format('&'.join(['{0}={1}'.format(x, data[x]) for x in data.keys()])) if data else ''
            request   = r_handler('{0}{1}'.format(path, query_str))
            
        # Request requires body data
        else:
            request = r_handler(path, json.dumps(data), content_type='application/json')
        
        # Default user / session object
        request.user = import_class('AnonymousUser', 'django.contrib.auth.models')
        request.session = import_class('SessionStore', 'django.contrib.sessions.backends.db')

        # Return the request object
        return request

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
        self.name       = self._getattr('username', header=HEADER.API_USER, default='anonymous')
        self.model      = self._getmodel()
 
        # User attributes
        self.group      = self._getattr('group', header=HEADER.API_GROUP, session='active_group', default='anonymous')
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
        model = import_class('APIUser', 'lense.common.objects.user.models', init=False)
        
        # Return the user model
        if model.objects.filter(username=self.name).count():
            return model.objects.get(username=self.name)
        return None
    
    def _getattr(self, key, default=None, header=None, session=None, model=False, post=False):
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
        if model and self.model:
            return getattr(self.model, key, default)
            
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
            self.USER.name,
            self.USER.group,
            self.key,
            self.token,
            truncate(str(self.data))
        ))
    
    def _load_data(self):
        """
        Load request data depending on the method. For POST requests, load the request
        body, for GET requests, load the query string.
        """
        try:
            
            # PUT/POST requests
            if self.method in [HTTP_POST, HTTP_PUT]:
                return LENSE.HTTP.parse_request_body(getattr(self.DJANGO, 'body', '{}'))
            
            # GET/DELETE requests
            else:
                return LENSE.HTTP.parse_query_string(self.DJANGO.META['QUERY_STRING'])
        
        # Error while parsing JSON
        except ValueError as e:
            raise RequestError(LENSE.LOG.exception('Failed to parse request data: {0}'.format(str(e))))
    
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
    
    def _get_header_value(self, key, default=None, regex=None):
        """
        Extract a value from the request headers.
        
        :param     key: The header hey to extract
        :type      key: str
        :param default: The default value to return if none found
        :type  default: mixed
        :param   regex: An optional compiled regex to extract a match from
        :type    regex: SRE_Pattern (i.e., re.compile())
        """
        header_value = self.DJANGO.META.get(key, default)
        
        # Default value found
        if header_value == default:
            return header_value
        
        # If passing through a regex
        if regex:
            return regex.sub(r'\g<1>', header_value)
        return header_value
    
    def map_data(self, keys):
        """
        Map request data to a dictionary by keys.
        """
        return {k:LENSE.REQUEST.data.get(k) for k in keys}
    
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
    
    def ensure(self, *args, **kwargs):
        """
        Raise a RequestError if ensure fails.
        """
        kwargs['exc'] = RequestError
        return LENSE.ensure(*args, **kwargs)
    
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
        self.path         = self._get_header_value('PATH_INFO', regex=compile(r'^\/?(.*$)'))
        self.client       = self._get_header_value('REMOTE_ADDR')
        self.host         = self._get_header_value('HTTP_HOST').split(':')[0]
        self.agent        = self._get_header_value('HTTP_USER_AGENT')
        self.query        = self._get_header_value('QUERY_STRING')
        self.script       = self._get_header_value('SCRIPT_NAME')
        self.current      = self._get_header_value('REQUEST_URI')
        
        # Request size / payload
        self.size         = int(getsizeof(getattr(request, 'body', '')))
        self.data         = self._load_data()
    
        LENSE.LOG.debug('Request data: type={0}, content={1}'.format(type(self.data), self.data))
    
        # Request user / session
        self.USER         = LenseRequestUser(request)
        self.SESSION      = LenseRequestSession(request.session)
    
        # Anonymous / token request boolean flags
        self.is_anonymous = True if not self.USER.name else False
        self.is_token     = True if (self.path == PATH.GET_TOKEN) else False
    
        # API key / token
        self.key          = self._get_key()
        self.token        = self._get_token()
        
        # Method / GET / POST / body data
        self._GET         = Collection(request.GET).get()
        self._POST        = Collection(request.POST).get()
        self.body         = request.body
    
        # Setup authentication
        LENSE.SETUP.auth()
    
        # Debug logging for each request
        self._log_request()