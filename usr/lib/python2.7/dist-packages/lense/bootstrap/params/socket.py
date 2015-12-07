from collections import OrderedDict

# Lense Libraries
from lense.bootstrap.common import BootstrapInput

class _SocketInput(BootstrapInput):
    """
    Handle user input prompts and responses
    """
    def __init__(self):
        self.prompt   = self.load_prompts('socket')
        self.response = {}

    def set_response(self, key, value=None):
        """
        Set a response definition.
        """
        self.response[key] = value

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