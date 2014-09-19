class AgentAPI:
    """
    API module for handling access to the host agent utilities.
    """
    def __init__(self, parent):
        self.parent = parent

    def poll(self, data=None):
        """
        API method for uploading polling data.
        """
        return self.parent._post('agent/poll', data=data)
    
    def system(self, data=None):
        """
        API method for uploading system information.
        """
        return self.parent._post('agent/system', data=data)
    
    def status(self, data=None):
        """
        API method for updating the agent run status.
        """
        return self.parent._post('agent/status', data=data)
    
    def formula(self, data=None):
        """
        API method for uploading formula run results.
        """
        return self.parent._post('agent/formula', data=data)
    
    def sync(self, params=None):
        """
        API method for retrieving synchronization data.
        """
        return self.parent._get('agent/sync', params=params)