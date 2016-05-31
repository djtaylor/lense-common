from __future__ import print_function
import sys
import json
import traceback

# Django Libraries
from django.core.serializers.json import DjangoJSONEncoder
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError

# Lense Libraries
from lense.common.collection import Collection

# Error codes to message mappings
ERR_MESSAGE = {
    500: 'An internal server error occurred, please contact your administrator',
    400: 'An error occurred while validating the request',
    401: 'An error occured while authorizing the request'
}

# HTTP methods
HTTP_GET     = 'GET'
HTTP_PUT     = 'PUT'
HTTP_POST    = 'POST'
HTTP_DELETE  = 'DELETE'

# All HTTP methods
HTTP_METHODS = [HTTP_GET, HTTP_PUT, HTTP_POST, HTTP_DELETE]

# HTTP Paths
PATH = Collection({
    'GET_TOKEN':    'token'
}).get()

# Format Lense header
def HEADER_FORMAT(header):
    return 'HTTP_{0}'.format(header.upper().replace('-', '_'))

# HTTP Headers
HEADER = Collection({
    'API_USER':     'Lense-API-User',
    'API_KEY':      'Lense-API-Key',
    'API_TOKEN':    'Lense-API-Token',
    'API_GROUP':    'Lense-API-Group',
    'API_ROOM':     'Lense-API-Room',
    'API_CALLBACK': 'Lense-API-Callback',
    'CONTENT_TYPE': 'Content-Type',
    'ACCEPT':       'Accept' 
}).get()

# MIME Types
MIME_TYPE = Collection({
    'TEXT': {
        'HTML':         'text/html',
        'CSS':          'text/css',
        'CSV':          'text/csv',
        'PLAIN':        'text/plain',
        'RTF':          'text/rtf'
    },
    'APPLICATION': {
        'XML':          'application/xml',
        'JSON':         'application/json',
        'STREAM':       'application/octet-stream',
        'OGG':          'application/ogg',
        'POSTSCRIPT':   'application/postscript',
        'RDF_XML':      'application/rdf+xml',
        'RSS_XML':      'application/rss+xml',
        'SOAP_XML':     'application/soap+xml',
        'FONT_WOFF':    'application/font-woff',
        'XHTML_XML':    'application/xhtml+xml',
        'ATOM_XML':     'application/atom+xml',
        'XML':          'application/xml',
        'XML_DTD':      'application/xml-dtd',
        'ECMASCRIPT':   'application/ecmascript',
        'PDF':          'application/pdf',
        'ZIP':          'application/zip',
        'GZIP':         'application/gzip',
        'JAVASCRIPT':   'application/javascript'
    }
}).get()

class JSONSuccess(object):
    """
    Base class for successfull request responses.
    """
    def __init__(self, msg, data):
        try:
            response = { 'message': msg, 'data': LENSE.OBJECTS.dump(data) }
        except:
            response = { 'message': msg, 'data': data }

        # If a callback is specified
        if LENSE.REQUEST.callback:
            response['callback'] = LENSE.REQUEST.callback

        # Response body
        self.body = json.dumps(response, cls=DjangoJSONEncoder)

    def response(self):
        """
        Construct and return the HTTP 200 response.
        """
        return HttpResponse(self.body, content_type=MIME_TYPE.APPLICATION.JSON, status=200)

class JSONErrorBase(object):
    """
    Base response class for error and exception responses.
    """
    def __init__(self, error=None, status=500, exception=False):

        # Store the response status code
        self.status = status

        # Construct the JSON error object
        self.error_object = {
            'message': ERR_MESSAGE.get(self.status, 'An unknown error has occurred, please contact your administrator'),
            'error':   error if not isinstance(error, (list, dict)) else json.dumps(error)
        }
        
        # If an error message is provided
        if error and isinstance(error, (str, unicode, basestring)):
            LENSE.LOG.error(error)
        
        # If providing a stack trace for debugging and debugging is enabled
        if exception and LENSE.CONF.engine.debug:
            self.error_object.update({
                'debug': self._extract_trace()
            })
    
    def _extract_trace(self):
        """
        Extract traceback details from an exception.
        """
        
        # Get the exception data
        try:
            e_type, e_info, e_trace = sys.exc_info()
        
            # Exception message
            e_msg = '{}: {}'.format(e_type.__name__, e_info)
        
            # Log the exception
            LENSE.LOG.exception(e_msg)
        
            # Return the exception message and traceback
            return {
                'exception': e_msg,
                'traceback': traceback.extract_tb(e_trace)
            }
            
        # Failed to extract exception data
        except:
            return None
        
    def response(self):
        """
        Construct and return the response object.
        """
        return HttpResponse(json.dumps(self.error_object), content_type=MIME_TYPE.APPLICATION.JSON, status=self.status)

class JSONError(JSONErrorBase):
    """
    Client error response object.
    """
    def __init__(self, error=None, status=400):
        super(JSONError, self).__init__(error=error, status=status)
    
class JSONException(JSONErrorBase):
    """
    Internal server error response object.
    """
    def __init__(self, error=None):
        super(JSONException, self).__init__(error=error, exception=True)
        
class LenseHTTP(object):
    """
    Common class for handling HTTP attributes, requests, and responses.
    """
    @staticmethod
    def parse_query_string(query_str):
        """
        Parse request data from a query string in the request URL.
        """
        data = {}
        
        # No query string
        if not query_str: return data
        
        # Process each query string key
        for query_pair in query_str.split('&'):
            
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
                
        # Return constructed data
        return data
    
    @staticmethod
    def redirect(path, data=None):
        """
        Return an HTTP redirect object.
        """
        return HttpResponseRedirect('/{0}{1}'.format(path, '' if not data else '?{0}'.format(data)))
    
    @staticmethod
    def success(msg='OK', data={}):
        """
        Return HTTP 200 and response message/data.
        
        :param  msg: The response message to send
        :type   msg: str
        :param data: Additional response data
        :type  data: str|dict|list
        :rtype: JSONSuccess
        """
        return JSONSuccess(msg=msg, data=data).response()
    
    @staticmethod
    def browser_error(template, data):
        """
        Return a error to the browser for rendering.
        """
        
        # Template / request object
        t = loader.get_template(template)
        r = LENSE.REQUEST.DJANGO
        
        # Return and render the error template
        return HttpResponseServerError(t.render(RequestContext(r, data)))
    
    @staticmethod
    def error(msg=None, status=400):
        """
        Return a JSON error message in an HTTP response object.
        
        :param    msg: The error message to return
        :type     msg: str
        :param status: The HTTP status code
        :type  status: int
        :rtype: JSONError
        """
        return JSONError(error=msg, status=status).response()
    
    @staticmethod
    def exception(msg=None):
        """
        Return a JSON error message raised by an exception (i.e., 500)
        
        :param msg: The error message to return
        :type  msg: str
        :rtype: JSONException
        """
        return JSONException(error=msg).response()