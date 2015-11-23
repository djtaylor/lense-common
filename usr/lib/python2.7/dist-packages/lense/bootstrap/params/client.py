from collections import OrderedDict

# Lense Libraries
from lense.common.vars import G_ADMIN, U_ADMIN

class _ClientInput(object):
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
        
        # Return the prompt object
        return _prompt

class ClientParams(object):
    """
    Bootstrap parameters class object used to store and set the attributes
    required when using the bootstrap manager for the Lense API client.
    """
    def __init__(self):
        
        # User input
        self.input  = _ClientInput()
    
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