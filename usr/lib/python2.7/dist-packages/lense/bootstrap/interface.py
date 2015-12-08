from re import compile
from os import environ, path
from feedback import Feedback
from collections import OrderedDict
from json import loads as json_loads

# Django Libraries
from django.conf import Settings
from django import setup as django_setup
from django.conf import settings as django_settings

# Lense Libraries
from lense import import_class
from lense.common import init_project
from lense.bootstrap.args import BootstrapArgs
from lense.bootstrap.common import BootstrapCommon
from lense.bootstrap.answers import BootstrapAnswers
from lense.common.request import LenseWSGIRequest

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
            
    def _bootstrap_engine(self):
        """
        Helper method to see if we are bootstrapping the Lense Engine, which
        requires database connection settings.
        """
        
        # Explicity bootstrapping Engine
        if self.args.get('engine'):
            return True
            
        # Bootstrapping all
        bootstrap_all = True
        for k in ['engine', 'client', 'portal', 'socket']:
            if self.args.get(k, False):
                bootstrap_all = False
        return bootstrap_all
            
    def _bootstrap_project(self, project):
        """
        Bootstrap a specific project.
        """
        interfaces = {
            'engine': 'BootstrapEngine',
            'portal': 'BootstrapPortal',
            'client': 'BootstrapClient',
            'socket': 'BootstrapSocket'
        }
        
        # Run the project bootstrap method
        if project in interfaces:
            project_attrs = interfaces[project]
            project_cls   = project_attrs if isinstance(project_attrs, str) else project_attrs[0]
            
            # Run the project bootstrap manager
            BOOTSTRAP.FEEDBACK.info('Running bootstrap manager for Lense project: {0}'.format(project))
            import_class(project_cls, 'lense.bootstrap.projects', args=[self.args, self.answers]).run()
          
    def _dbinit(self):
        """
        Initialize bootstrap Django settings.
        """
        fb = Feedback()
        
        # Attribute mappings
        env_attrs = json_loads(open('/usr/share/lense/bootstrap/dbinit.json', 'r').read())
        
        # Bootstrapping the engine requires a database connection
        if self._bootstrap_engine():
            dbinit_file = self.args.get('dbinit')
            
            # If loading from a file
            if dbinit_file and path.isfile(dbinit_file):
                fb.info('Initializing database parameters from file: {0}'.format(dbinit_file))
                with open(dbinit_file, 'r') as f:
                    for l in f.readlines():
                        env_var = compile(r'(^[^=]*)=.*$').sub(r'\g<1>', l.rstrip())
                        env_val = compile(r'^[^=]*=\"([^\"]*)\"$').sub(r'\g<1>', l.rstrip())
                        
                        # Set the environment variable
                        if env_var in env_attrs:
                            fb.success('Setting environment variable: {0}'.format(env_var))
                            environ[env_var] = env_val
                        else:
                            fb.warn('Unsupported environment variable: {0}'.format(env_var))
            
            # Full interactive database initialization
            else:
                fb.block([
                    'Bootstrapping the Lense Engine requires Django database settings.',
                    'Please fill out the following prompts to configure the database:'
                ], 'DBINIT')
            
            # Get connection attributes prior to bootstrapping
            for var_key, var_attrs in env_attrs.iteritems():
                if not environ.get(var_key, None):
                    fb.input(var_attrs['prompt'], var_attrs['key'], **var_attrs.get('kwargs', {}))
                    environ[var_key] == fb.get_response(var_attrs['key'])
            
        # Set the Django settings module
        environ['DJANGO_SETTINGS_MODULE'] = 'lense.bootstrap.settings'
        
        # Setup Django for the bootstrap run
        django_setup()
            
        # Register project commons
        init_project('BOOTSTRAP', 'BOOTSTRAP')
        init_project('ENGINE', 'LENSE')
            
    def _run(self):
        """
        Private method for starting up the bootstrap process.
        """
        
        # Get command line arguments
        self.args    = BootstrapArgs()
        
        # Initialize Django database settings
        self._dbinit()
        
        # Show bootstrap information
        self.bootstrap_info()
        
        # Get answer file
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
        return Bootstrap()._run()