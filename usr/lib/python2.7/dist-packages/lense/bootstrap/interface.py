from lense.common import LenseCommon
from lense.bootstrap.args import BootstrapArgs
from lense.bootstrap.answers import BootstrapAnswers
from lense.bootstrap.params import EngineParams, PortalParams, ClientParams, SocketParams
from lense.bootstrap.projects import BootstrapClient, BootstrapPortal, BootstrapEngine, BootstrapSocket

# Lense Common
LENSE = LenseCommon('BOOTSTRAP')

try:
    from lense.engine.api.base import APIBare
except:
    pass

class Bootstrap(BootstrapCommon):
    """
    Main class object for bootstrapping the Lense installation. This
    includes setting up the database and the admin user account.
    """
    def __init__(self):
        super(Bootstrap, self).__init__()
    
        # Arguments / answers
        self.args    = BootstrapArgs()
        self.answers = BootstrapAnswers(self.args.get('answers', None)).read()
            
    def _bootstrap_project(self, project):
        """
        Bootstrap a specific project.
        """
        interfaces = {
            'engine': BootstrapEngine,
            'portal': BootstrapPortal,
            'client': BootstrapClient,
            'socket': BootstrapSocket
        }
        
        # Run the project bootstrap method
        if project in interfaces:
            LENSE.FEEDBACK.info('Running bootstrap manager for Lense API {0}...\n'.format(project))
            interfaces[project]().run()
            
    def _run(self):
        """
        Private method for starting up the bootstrap process.
        """
        
        # Show bootstrap information
        self._bootstrap_info()
        
        # Bootstrap projects
        projects = {
            'engine': self.args.get('engine', False),
            'portal': self.args.get('portal', False),
            'client': self.args.get('client', False),
            'socket': self.args.get('socket', False)
        }
        
        # None selected, bootstrap everything
        if not [(None if not x in projects else x) for x in [
            'engine', 
            'portal', 
            'client', 
            'socket'
        ]]:
            results = [self._bootstrap_project(x) for x in projects]
            
        # Bootstrapping specific projects
        else:
            for project, run in projects.iteritems():
                if run: self._bootstrap_project(project)
            
    @staticmethod
    def run():
        """
        Public static method for invoking the bootstrap manager.
        """
        return Bootstrap()._run()