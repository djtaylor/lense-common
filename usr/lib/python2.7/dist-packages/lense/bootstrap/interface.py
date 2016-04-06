from os import environ
from collections import Mapping
from collections import OrderedDict
from json import loads as json_loads

# Django Libraries
from django import setup as django_setup

# Lense Libraries
from lense import import_class
from lense.common.vars import SHARE
from lense.common import init_project
from lense.bootstrap.args import BootstrapArgs
from lense.bootstrap.common import BootstrapCommon
from lense.bootstrap.answers import BootstrapAnswers

class Bootstrap(BootstrapCommon):
    """
    Main class object for bootstrapping the Lense installation. This
    includes setting up the database and the admin user account.
    """
    def __init__(self):
        super(Bootstrap, self).__init__('bootstrap')
            
    def _bootstrap_engine(self):
        """
        Helper method to see if we are bootstrapping the Lense Engine, which
        requires database connection settings.
        """
        
        # Explicity bootstrapping Engine
        if BOOTSTRAP.ARGS.get('engine'):
            return True
            
        # Bootstrapping all
        bootstrap_all = True
        for k in ['engine', 'client', 'portal', 'socket']:
            if BOOTSTRAP.ARGS.get(k, False):
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
            import_class(project_cls, 'lense.bootstrap.projects').run()
          
    def _init_db(self, answers):
        """
        Initialize bootstrap Django settings.
        """
        default_answers = json_loads(open('{0}/defaults/answers.json'.format(SHARE.BOOTSTRAP), 'r').read())
        default_keys = default_answers['init']['db']
        
        # Bootstrapping the engine requires a database connection
        if self._bootstrap_engine():
            BOOTSTRAP.FEEDBACK.info('[init][db] Initializing database')
            prompts = json_loads(open('{0}/prompts/init/database.json'.format(SHARE.BOOTSTRAP), 'r').read())
            
            # Answers supplied
            if answers:
                for k,v in answers.iteritems():
                    
                    # Unsupported key
                    if not k in default_keys:
                        BOOTSTRAP.FEEDBACK.warn('[init][db] Unsupported environment variable: {0}'.format(k))
                    
                    # Set the environment variable
                    environ[k] = v
                    BOOTSTRAP.FEEDBACK.success('[init][db] Set environment variable: {0}'.format(k))
            
            # Get connection attributes prior to bootstrapping
            for k,a in prompts.iteritems():
                if not environ.get(k, None):
                    BOOTSTRAP.FEEDBACK.input(a['prompt'], a['key'], **a.get('kwargs', {}))
                    environ[var_key] == BOOTSTRAP.FEEDBACK.get_response(a['key'])
            
    def _run(self):
        """
        Private method for starting up the bootstrap process.
        """
        
        # Set the Django settings module
        environ['DJANGO_SETTINGS_MODULE'] = 'lense.bootstrap.settings'
        
        # Setup Django for the bootstrap run
        django_setup()
            
        # Register project commons
        init_project('BOOTSTRAP', 'BOOTSTRAP')
        init_project('ENGINE', 'LENSE')
        
        # Store arguments / answers
        BOOTSTRAP.ARGS    = BootstrapArgs()
        BOOTSTRAP.ANSWERS = BootstrapAnswers.get(mapper={
            'db': self._init_db
        })
        
        # Show bootstrap information
        self.bootstrap_info()
        
        # Run the preflight bootstrap methods
        self.bootstrap_preflight()
        
        # Bootstrap projects
        projects = OrderedDict()
        projects['engine'] = BOOTSTRAP.ARGS.get('engine', False)
        projects['portal'] = BOOTSTRAP.ARGS.get('portal', False)
        projects['client'] = BOOTSTRAP.ARGS.get('client', False)
        projects['socket'] = BOOTSTRAP.ARGS.get('socket', False)
    
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
            
    @classmethod
    def run(cls):
        """
        Public class method for invoking the bootstrap manager.
        """
        return cls()._run()