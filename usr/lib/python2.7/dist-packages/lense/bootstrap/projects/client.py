from lense.bootstrap.params import ClientParams
from lense.bootstrap.common import BootstrapCommon

class BootstrapClient(BootstrapCommon):
    """
    Class object for handling bootstrap of the Lense API client.
    """
    def __init__(self, args, answers):
        super(BootstrapClient, self).__init__('client')

        # Arguments / answers
        self.args     = args
        self.answers  = answers

        # Bootstrap parameters
        self.params   = ClientParams()

    def _bootstrap_complete(self):
        """
        Brief summary of the completed bootstrap process.
        """
        
        # Print the summary
        BOOTSTRAP.FEEDBACK.block([
            'Finished bootstrapping Lense API client!\n',
            'You will need to add yourself to the "lense" group for write access',
            'to the client log:\n',
            'usermod -a -G lense <username>'
        ], 'COMPLETE')
        
    def run(self):
        
        # Get user input
        self.read_input(self.answers.get('client', {}))
        
        # Update the configuration
        self.update_config()
        
        # Set log permissions
        self.set_permissions(self.CONFIG.client.log, owner='lense:lense', mode='g+x')
        
        # Show the bootstrap complete summary
        self._bootstrap_complete()