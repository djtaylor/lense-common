from os import chdir, getcwd
from lense.bootstrap.params import SocketParams
from lense.bootstrap.common import BootstrapCommon

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

        # NPM module
        self.npm_mod  = 'git://github.com/djtaylor/lense-socket-npm.git'

    def npm_installed(self):
        """
        Check if the node module is installed.
        """
        command = ['npm', 'list', '--prefix', self.ATTRS.PREFIX, 'lense-socket-npm']
        code, err = self._shell_exec(command, show_stdout=False)

        # Installed
        if code == 0:
            return True
        return False

    def check_npm(self):
        """
        Make sure NPM packages are installed.
        """
        if not self.npm_installed():
            BOOTSTRAP.FEEDBACK.info('Installing NPM module: lense-socket-npm <{0}>'.format(self.npm_mod))
            command  = ['npm', 'install', '--prefix', self.ATTRS.PREFIX, self.npm_mod]
            code, err = self._shell_exec(command, show_stdout=False)
            
            # Package installation failed
            if not code == 0:
                self.die('Failed to install NPM module')
            BOOTSTRAP.FEEDBACK.success('Installed NPM module')
            
        # Package already installed
        else:
            BOOTSTRAP.FEEDBACK.info('Discovered NPM module: {0}/node_modules/lense-socket-npm'.format(self.ATTRS.PREFIX))

    def _bootstrap_complete(self):
        """
        Brief summary of the completed bootstrap process.
        """
        
        # Print the summary
        BOOTSTRAP.FEEDBACK.block([
            'Finished bootstrapping Lense API Socket.IO proxy server!\n',
            'You may enable and start the Socket.IO proxy server with the',
            'following commands:\n',
            'sudo update-rc.d lense-socket defaults',
            'sudo service lense-socket start'
        ], 'COMPLETE')
        
    def run(self):
        
        # Get user input
        self.read_input(self.answers.get('socket', {}))
        
        # Create required directories
        self.mkdirs([self.dirname(self.ATTRS.LOG), self.ATTRS.RUN])
        
        # Update the configuration
        self.update_config()
        
        # Ensure node modules
        self.check_npm()
        
        # Show the bootstrap complete summary
        self._bootstrap_complete()