from collections import OrderedDict

# Lense Libraries
from lense.common import init_project
from lense.bootstrap.args import BootstrapArgs
from lense.bootstrap.common import BootstrapCommon
from lense.bootstrap.answers import BootstrapAnswers
from lense.bootstrap.projects import BootstrapClient, BootstrapPortal, BootstrapEngine, BootstrapSocket

class Bootstrap(BootstrapCommon):
    """
    Main class object for bootstrapping the Lense installation. This
    includes setting up the database and the admin user account.
    """
    def __init__(self):
        super(Bootstrap, self).__init__('bootstrap')
        
        # Arguments / answers
        self.args    = None
        self.answers = None
            
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
            LENSE.FEEDBACK.info('Running bootstrap manager for Lense project: {0}\n'.format(project))
            interfaces[project](self.args, self.answers).run()
            
    def _run(self):
        """
        Private method for starting up the bootstrap process.
        """
        
        # Show bootstrap information
        self.bootstrap_info()
        
        # Get command line arguments and answer file
        self.args    = BootstrapArgs()
        self.answers = BootstrapAnswers(self.args.get('answers', None)).read()
        
        # Run the preflight bootstrap methods
        self.bootstrap_preflight()
        
        # Bootstrap projects
        projects = OrderedDict()
        projects['engine'] = self.args.get('engine', False)
        projects['portal'] = self.args.get('portal', False)
        projects['client'] = self.args.get('client', False)
        projects['socket'] = self.args.get('socket', False)
    
        # None selected, bootstrap everything
        if all(v is None for v in [(None if not projects[x] else x) for x in [
            'engine', 
            'portal', 
            'client', 
            'socket'
        ]]):
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
        
        # Register project commons
        init_project('BOOTSTRAP')
        
        # Run the bootstrap manager
        return Bootstrap()._run()