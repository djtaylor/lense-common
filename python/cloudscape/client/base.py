import sys
import json
import requests
import importlib

# CloudScape Libraries
from cloudscape.common.http import HEADER, MIME_TYPE
from cloudscape.common.vars import C_CLIENT
from cloudscape.common.utils import parse_response

class APIBase(object):
    """
    The base class inherited by API path specific classes. This class provides access to
    command methods to GET and POST data to the API server.
    """
    def __init__(self, user=None, group=None, token=None, url=None):

        # API User / Group / Token / URL / Headers
        self.API_USER    = user
        self.API_TOKEN   = token
        self.API_GROUP   = group
        self.API_URL     = url
        self.API_HEADERS = self._construct_headers()

        # Construct the API map
        self._construct_map()

    def _construct_headers(self):
        """
        Construct the request authorization headers.
        """
        return {
            HEADER.CONTENT_TYPE: MIME_TYPE.APPLICATION.JSON,
            HEADER.ACCEPT:       MIME_TYPE.TEXT.PLAIN,
            HEADER.API_USER:     self.API_USER,
            HEADER.API_TOKEN:    self.API_TOKEN,
            HEADER.API_GROUP:    self.API_GROUP
        }

    def _construct_map(self):
        """
        Method to construct the API request objects.
        """

        # Load the mapper JSON manifest
        map_json = None
        with open('%s/mapper.json' % C_CLIENT, 'r') as f:
            map_json = json.loads(f.read())

        # Set the modules base
        mod_base = map_json['base']
        
        # Load each module
        for mod in map_json['modules']:
            api_mod = '%s.%s' % (mod_base, mod['module'])
            
            # Load the API endpoint handler
            ep_mod   = importlib.import_module(api_mod)
            ep_class = getattr(ep_mod, mod['class'])
            ep_inst  = ep_class(self)
            
            # Set the internal attribute
            setattr(self, mod['id'], ep_inst)

    def _get(self, path, params={}):
        """
        Wrapper method to make GET requests to the specific API endpoint.
        """
        
        # Set the request URL to the API endpoint path
        get_url = '%s/%s' % (self.API_URL, path)
        
        # POST the request and return the response
        return parse_response(requests.get(get_url, headers=self.API_HEADERS, params=params))

    def _post(self, path, data={}, params={}):
        """
        Wrapper method to make POST requests to the specific API endpoint.
        """
        
        # Set the request URL to the API endpoint path
        post_url = '%s/%s' % (self.API_URL, path)
        
        # POST the request and return the response
        return parse_response(requests.post(post_url, data=json.dumps(data), headers=self.API_HEADERS, params=params))