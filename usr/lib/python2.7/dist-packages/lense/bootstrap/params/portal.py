from collections import OrderedDict

# Lense Libraries
from lense.common.utils import rstring
from lense.bootstrap.common import BootstrapInput

class PortalParams(object):
    """
    Bootstrap parameters class object used to store and set the attributes
    required when using the bootstrap manager for the Lense API portal.
    """
    def __init__(self):
        
        # User input
        self.input  = BootstrapInput('portal')
    
    def get_config(self):
        """
        Load the updated server configuration
        """
        
        # Generate a new Django secret
        django_secret = "'{0}'".format(rstring(64))
        
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
            'db': {
                'host': self.input.response.get('db_host'),
                'port': self.input.response.get('db_port'),
                'user': self.input.response.get('db_user'),
                'password': self.input.response.get('db_user_password'),
                'name': self.input.response.get('db_name')
            },
            'portal': {
                'host': self.input.response.get('portal_host'),
                'port': self.input.response.get('portal_port'),
                'secret': django_secret
            },
            'socket': {
                'host': self.input.response.get('socket_host'),
                'port': self.input.response.get('socket_port')
            }    
        }