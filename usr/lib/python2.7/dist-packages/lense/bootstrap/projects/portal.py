from lense.bootstrap.params import PortalParams
from lense.bootstrap.common import BootstrapCommon

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
        
        # Update the configuration
        self.update_config()
            
        # Deploy the Apache configuration
        self.deploy_apache()
            
        # Set log file permissions
        self.set_permissions(self.ATTRS.LOG, owner='www-data:www-data')
        
        # Add the Apache user to the lense group
        self.group_add_user('www-data')
            
        # Show to bootstrap complete summary
        self._bootstrap_complete()