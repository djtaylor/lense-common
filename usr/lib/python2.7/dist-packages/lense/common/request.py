import json
from copy import copy
from re import compile
from sys import getsizeof
from urllib import unquote
from six import string_types
from uuid import uuid4

# Django Libraries
from django.test.client import RequestFactory

# Lense Libraries
from lense import import_class
from lense.common import logger
from lense.common.utils import truncate
from lense.common.collection import Collection, merge_dict
from lense.common.exceptions import RequestError
from lense.common.http import HTTP_GET, HTTP_POST, HTTP_PUT, HEADER, PATH, HEADER_FORMAT
from django.template.defaultfilters import default

class LenseRequestBase(object):
    """
    Base class for request related class objects.
    """
    def __init__(self):
        self.logpre = 'REQUEST:{0}'.format(self.__class__.__name__)

    def log(self, msg, level='info', method=None):
        """
        Log wrapper per handler.
        """
        logger = getattr(LENSE.LOG, level, 'info')
        logger('<{0}{1}> {2}'.format(
            self.logpre,
            '' if not method else '.{0}'.format(method),
            msg
        ))

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

class LenseRequestSession(LenseRequestBase):
    """
    Helper class for handling session attributes.
    """
    def __init__(self, session):
        super(LenseRequestSession, self).__init__()

        # Store session object
        self._session = session

        # Session ID
        self.id       = getattr(session, 'session_key', None)

        # Log the session attributes
        self.log('Loading session "{0}" data: {1}'.format(self.id, dict(session)), level='debug', method='__init__')

    def __repr__(self):
        return '<LenseRequestSession({0})>'.format(self.id)

    def set(self, key, value):
        """
        Set a new session value or update an existing one
        """
        self._session[key] = value
        self.log('Setting session key: {0}={1}'.format(key, value), level='debug', method='set')

    def get(self, key, default=None):
        """
        Retrieve a session value.
        """
        key_value = getattr(self._session, key, default)
        self.log('Retrieving session key: {0}={1}'.format(key, key_value), level='debug', method='get')
        return key_value

class LenseRequestUser(LenseRequestBase):
    """
    Helper class for extracting and storing user attributes.
    """
    def __init__(self, request):
        super(LenseRequestUser, self).__init__()

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
        self.room       = self._getattr('room', header=HEADER.API_ROOM)
        self.uuid       = self._getattr('uuid', default=None, model=True)

        # Log user details
        self.log('Constructed request user object: name={0}, group={1}, authorized={2}, admin={3}, active={4}'.format(
            self.name,
            self.group,
            self.authorized,
            self.admin,
            self.active
        ), level='debug', method='__init__')

    def __repr__(self):
        return '<LenseRequestUser({0})>'.format(self.uuid)

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
        if header and HEADER_FORMAT(header) in self._request.META:
            return self._request.META.get(HEADER_FORMAT(header), default)

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

class LenseRequestObject(LenseRequestBase):
    """
    Extract and construct information from the Django request object.
    """
    def _log_request(self):
        """
        Log incoming requests to the request log.
        """
        self.log('method={0}, path={1}, client={2}, user={3}, group={4}, key={5}, token={6}, data={7}'.format(
            self.method,
            self.path,
            self.client,
            self.USER.name,
            self.USER.group,
            self.key,
            self.token,
            truncate(str(self.data))
        ), level='debug', method='_log_request')

    def _parse_data(self, data_str):
        """
        Parse a data query string or request body.
        """
        if not data_str:
            return {}

        # Try JSON first
        try:
            data_obj = json.loads(data_str)
            self.log('Parsed JSON request data: {0}'.format(data_str), level='debug', method='_parse_data')
            return data_obj

        # Query string?
        except Exception as e:
            try:
                data_obj = LENSE.HTTP.parse_query_string(data_str)
                self.log('Parsed query string request data: {0}'.format(data_str), level='debug', method='_parse_data')
                return data_obj

            # Request body not query string or JSON string
            except Exception as e:
                self.log('Failed to parse data string ({0}): {1}'.format(data_str, str(e)), level='exception', method='_parse_data')
                return {}

    def _load_data(self):
        """
        Load request data depending on the method. For POST requests, load the request
        body, for GET requests, load the query string.
        """

        # Extract request body / query string
        request_body  = getattr(self.DJANGO, 'body', '{}')
        request_query = self.DJANGO.META.get('QUERY_STRING', '')

        # Log incoming data
        self.log('Processing request data: body=({0}), query_string=({1})'.format(request_body, request_query), level='debug', method='_load_data')

        # Return an request data
        try:
            merged_data = merge_dict(
                self._parse_data(request_body),
                self._parse_data(request_query)
            )

            # Decode any HTML entities and bool strings
            self.log('Decoding HTML/boolean entities', level='debug', method='_load_data')
            for k,v in merged_data.iteritems():
                if isinstance(v, string_types):
                    merged_data[k] = unquote(v).decode('utf8')
                if (v in ['True', 'False']):
                    merged_data[k] = True if (v == 'True') else False

        # Failed to merge data, key conflict
        except Exception as e:
            raise RequestError('Failed to parse request data: {0}'.format(str(e)), code=400)
            return {}

        # Log the merged data and return
        self.log('Loaded request data: {0}'.format(json.dumps(merged_data)), level='debug', method='_load_data')
        return merged_data

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
        super(LenseRequestObject, self).__init__()

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

        # Portal request attributes
        self.view         = self.GET('view', None)
        self.callback     = self._get_header_value(HEADER_FORMAT(HEADER.API_CALLBACK))

        # Request UUID
        self.uuid         = str(uuid4())

        # Setup authentication
        LENSE.SETUP.auth()

        # Debug logging for each request
        self._log_request()
