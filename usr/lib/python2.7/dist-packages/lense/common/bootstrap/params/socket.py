from collections import OrderedDict

# Lense Libraries
from lense.common.vars import G_ADMIN, U_ADMIN

class _SocketInput(object):
    """
    Handle user input prompts and responses
    """
    def __init__(self):
        self.prompt   = self._set_prompts()
        self.response = {}

    def set_response(self, key, value=None):
        """
        Set a response definition.
        """
        self.response[key] = value

    def _set_prompts(self):
        """
        Set attributes for input prompts.
        """
        
        # Prompt collection
        _prompt = OrderedDict()
        
        # Administrator entries
        _prompt['admin'] = {
            "label": "API Administrator Configuration",
            "attrs": OrderedDict({
                "admin_user": {
                    "type": "str",
                    "default": "lense",
                    "prompt": "Please enter the API administrator username (lense): ",
                    "value": None
                },
                "admin_group": {
                    "type": "str",
                    "default": G_ADMIN,
                    "prompt": "Please enter the group UUID for the API administrator ({0}): ".format(G_ADMIN),
                    "value": None
                },
                "admin_key": {
                    "type": "str",
                    "default": None,
                    "prompt": "Please enter the administrator API key generated during bootstrap: ",
                    "value": None
                }
            })
        }
        
        # API engine entries
        _prompt['engine'] = {
            "label": "API Engine Configuration",
            "attrs": OrderedDict({
                "engine_host": {
                    "type": "str",
                    "default": "localhost",
                    "prompt": "Please enter the hostname for the API server (localhost): ",
                    "value": None
                },
                "engine_port": {
                    "type": "str",
                    "default": "10550",
                    "prompt": "Please enter the port for the API server (10550): ",
                    "value": None
                } 
            })             
        }
        
        # API proxy socket server entries
        _prompt['socket'] = {
            "label": "API Socket.IO Proxy Configuration",
            "attrs": OrderedDict({
                "socket_host": {
                    "type": "str",
                    "default": "localhost",
                    "prompt": "Please enter the hostname for the socket server (localhost): ",
                    "value": None
                },
                "socket_port": {
                    "type": "str",
                    "default": "10551",
                    "prompt": "Please enter the port for the socket server (10551): ",
                    "value": None
                },
                "socket_bind_ipaddr": {
                    "type": "str",
                    "default": "127.0.0.1",
                    "prompt": "Please enter the bind IP address for the socket server (127.0.0.1): ",
                    "value": None
                }
            })             
        }
        
        # Return the prompt object
        return _prompt

class SocketParams(object):
    """
    Bootstrap parameters class object used to store and set the attributes
    required when using the bootstrap manager for the Lense API socket proxy.
    """
    def __init__(self):
        
        # User input
        self.input  = _SocketInput()
    
    def get_config(self):
        """
        Load the updated server configuration
        """
        
        # Return the updated server configuration
        return {
            'admin': {
                'user': self.input.response.get('admin_user'),
                'group': self.input.response.get('admin_group'),
                'key': self.input.response.get('admin_key')
            },
            'engine': {
                'host': self.input.response.get('engine_host'),
                'port': self.input.response.get('engine_port')     
            },
            'socket': {
                'host': self.input.response.get('socket_host'),
                'port': self.input.response.get('socket_port'),
                'bind_ip': self.input.response.get('socket_bind_ipaddr')
            }  
        }