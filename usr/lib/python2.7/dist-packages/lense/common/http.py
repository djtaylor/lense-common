from __future__ import print_function
import sys
import json
import traceback

# Django Libraries
from django.http import HttpResponse

# Lense Libraries
from lense.common import config
from lense.common import logger
from lense.common.collection import Collection

# Error codes to message mappings
ERR_MESSAGE = {
    500: 'An internal server error occurred, please contact your administrator',
    400: 'An error occurred while validating the request',
    401: 'An error occured while authorizing the request'
}

# HTTP methods
HTTP_GET = 'GET'
HTTP_PUT = 'PUT'
HTTP_POST = 'POST'
HTTP_DELETE = 'DELETE'

# HTTP Paths
PATH = Collection({
    'GET_TOKEN':    'gateway/token'
}).get()

# HTTP Headers
HEADER = Collection({
    'API_USER':     'CS-API-User',
    'API_KEY':      'CS-API-Key',
    'API_TOKEN':    'CS-API-Token',
    'API_GROUP':    'CS-API-Group',
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

def error_response(message, response=None, cli=False):
    """
    Helper method used to handle a returned error response.
    
    :param message:  The error message to display
    :type message:   str
    :param response: A Python response object
    :type response:  obj
    :param cli:      Boolean indicating if being called from a command line client
    :type cli:       bool
    """
    
    # If being run from the command line
    if cli:
        
        # Show the error message
        print('ERROR: {}'.format(message))
        
        # Show any problems with token retrieval
        if response:
            rsp_msg = response['body'].get('message', 'Failed to process the request')
            rsp_err = response['body'].get('error', 'An unknown error has occurred')
            
            # Print the response
            print('\n---RESPONSE---')
            print('HTTP {}: {}\n'.format(response['code'], '{} - {}'.format(rsp_msg, rsp_err)))
            
            # If any debug information is present
            if 'debug' in response['body']:
                print('---DEBUG---')
                print('Traceback (most recent call last):')
                for l in response['body']['debug']['traceback']:
                    print('  File "{}", line {}, in {}'.format(l[0], l[1], l[2]))
                    print('    {}'.format(l[3]))
                print('Exception: {}\n'.format(response['body']['debug']['exception']))
        
        # Exit the client
        sys.exit(1)
        
    # Library is being loaded from another module
    else:
        return response

def parse_response(obj):
    """
    Helper method used to parse a Python requests object and return a formatted dictionary.
    Used to help alleviate differences between versions of the requests module on different
    systems.
    
    :param obj: The response object to parse
    :type obj: object
    :rtype: dict
    """
    return_obj = {}
    
    # Look for the status code
    if hasattr(obj, 'status_code'):
        return_obj['code'] = obj.status_code
    if hasattr(obj, 'code'):
        return_obj['code'] = obj.code
    
    # Look for the return body
    if hasattr(obj, 'content'):
        return_obj['body'] = obj.content
    if hasattr(obj, 'text'):
        if callable(getattr(obj, 'text')):
            return_obj['body'] = obj.text()
        else:
            return_obj['body'] = obj.text
    
    # Return the formatted response
    return return_obj

class JSONErrorBase(object):
    """
    Base response class for error and exception responses.
    """
    def __init__(self, error=None, status=500, exception=False):

        # Configuration / logger
        self.conf = config.parse()
        self.log  = logger.create(__name__, self.conf.server.log)

        # Store the response status code
        self.status = status

        # Construct the JSON error object
        self.error_object = {
            'message': ERR_MESSAGE.get(self.status, 'An unknown error has occurred, please contact your administrator'),
            'code':    self.status,
            'error':   error if not isinstance(error, (list, dict)) else json.dumps(error)
        }
        
        # If an error message is provided
        if error and isinstance(error, (str, unicode, basestring)):
            self.log.error(error)
        
        # If providing a stack trace for debugging and debugging is enabled
        if exception and self.conf.server.debug:
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
            self.log.exception(e_msg)
        
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