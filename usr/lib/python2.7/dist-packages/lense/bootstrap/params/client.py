from collections import OrderedDict

class _ClientInput(object):
    """
    Handle user input prompts and responses
    """
    def __init__(self):
        self.prompt   = self.load_prompts('client')
        self.response = {}

    def set_response(self, key, value=None):
        """
        Set a response definition.
        """
        self.response[key] = value

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