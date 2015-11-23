from lense.common import LenseCommon
from lense.bootstrap.params import PortalParams
from lense.bootstrap.common import BootstrapCommon

# Lense Common
LENSE = LenseCommon('BOOTSTRAP')

class BootstrapPortal(BootstrapCommon):
    """
    Class object for handling bootstrap of the Lense API portal.
    """
    def __init__(self, args, answers):
        super(BootstrapPortal, self).__init__('portal')

        # Arguments / answers
        self.args     = args
        self.answers  = answers
        
        # Bootstrap parameters
        self.params   = PortalParams()

    def _bootstrap_complete(self):
        """
        Brief summary of the completed bootstrap process.
        """
        
        # Print the summary
        LENSE.FEEDBACK.block([
            'Finished bootstrapping Lense API portal!\n',
            'You should restart your Apache service to load the new virtual host',
            'configuration. You can connect to the Lense API portal using the',
            'administrator credentials generated during the engine bootstrap process',
            'at the following URL:\n',
            'http://{0}:{1}'.format(self.params.input.response.get('portal_host'), self.params.input.response.get('portal_port'))
        ], 'COMPLETE')
        
    def run(self):
            
        # Get user input
        self.read_input(self.answers.get('portal', {}))
        
        # Create required directories and update the configuration
        self.mkdirs([self.get_file_path(self.ATTRS.LOG)])
        self.update_config('portal')
            
        # Deploy the Apache configuration
        self.deploy_apache('portal')
            
        # Set log file permissions
        self.chown_logs('portal', user='www-data', group='www-data')
        self.group_add_user('www-data')
            
        # Show to bootstrap complete summary
        self._bootstrap_complete()