from lense.common import LenseCommon
from lense.bootstrap.params import SocketParams
from lense.bootstrap.common import BootstrapCommon

# Lense Common
LENSE = LenseCommon('BOOTSTRAP')

class BootstrapSocket(BootstrapCommon):
    """
    Class object for handling bootstrap of the Lense API Socket.IO proxy.
    """
    def __init__(self, args, answers):
        super(BootstrapSocket, self).__init__('socket')

        # Arguments / answers
        self.args     = args
        self.answers  = answers

        # Bootstrap parameters
        self.params   = SocketParams()

    def _bootstrap_complete(self):
        """
        Brief summary of the completed bootstrap process.
        """
        
        # Print the summary
        LENSE.FEEDBACK.block([
            'Finished bootstrapping Lense API Socket.IO proxy server!\n',
            'You may enable and start the Socket.IO proxy server with the',
            'following commands:\n',
            'sudo update-rc.d lense-socket defaults',
            'sudo service lense-socket start\n',
            'The Socket.IO proxy also looks for a few non-standard modules',
            'which should be installed with the following command:\n',
            'sudo npm install --prefix /usr/share/lense/socket socket.io winston'
        ], 'COMPLETE')
        
    def run(self):
        
        # Get user input
        self.read_input(self.answers.get('socket', {}))
        
        # Create required directories
        self.mkdirs([self.get_file_path(self.ATTRS.LOG), self.get_file_path(self.ATTRS.RUN)])
        
        # Update the configuration
        self.update_config('socket')
        
        # Show the bootstrap complete summary
        self._bootstrap_complete()