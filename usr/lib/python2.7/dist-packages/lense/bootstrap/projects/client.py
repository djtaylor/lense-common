from lense.common import LenseCommon
from lense.bootstrap.params import ClientParams
from lense.bootstrap.common import BootstrapCommon

# Lense Common
LENSE = LenseCommon('BOOTSTRAP')

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
        LENSE.FEEDBACK.block([
            'Finished bootstrapping Lense API client!'
        ], 'COMPLETE')
        
    def run(self):
        
        # Get user input
        self.read_input(self.answers.get('client', {}))
        
        # Create required directories and update the configuration
        self.mkdirs([self.get_file_path(self.ATTRS.LOG)])
        self.update_config('client')
        
        # Show the bootstrap complete summary
        self._bootstrap_complete()