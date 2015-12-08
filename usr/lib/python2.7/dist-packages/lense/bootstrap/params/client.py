from collections import OrderedDict

# Lense Libraries
from lense.bootstrap.common import BootstrapInput

class ClientParams(object):
    """
    Bootstrap parameters class object used to store and set the attributes
    required when using the bootstrap manager for the Lense API client.
    """
    def __init__(self):
        
        # User input
        self.input  = BootstrapInput('client')
    
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
            } 
        }