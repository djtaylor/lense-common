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
from lense.common.collection import merge_dict
from lense.bootstrap.args import BootstrapArgs
from lense.bootstrap.common import BootstrapCommon
from lense.bootstrap.answers import BootstrapAnswers
from lense.common.request import LenseWSGIRequest

# Share directory
LENSE_SHARE = '/usr/share/lense/bootstrap'

class Bootstrap(BootstrapCommon):
    """
    Main class object for bootstrapping the Lense installation. This
    includes setting up the database and the admin user account.
    """
    def __init__(self):
        super(Bootstrap, self).__init__('bootstrap')
        
        # Arguments / answers / feedback
        self.args    = None
        self.answers = None
        self.fb      = Feedback()
            
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
          
    def _init_db(self, answers):
        """
        Initialize bootstrap Django settings.
        """
        default_answers = json_loads(open('{0}/defaults/answers.json'.format(LENSE_SHARE), 'r').read())
        default_keys = default_answers.get('db')
        
        # Bootstrapping the engine requires a database connection
        if self._bootstrap_engine():
            self.fb.info('[init][db] Initializing database')
            prompts = json_loads(open('{0}/bootstrap/prompts/database.json'.format(LENSE_SHARE), 'r').read())
            
            # Answers supplied
            if answers:
                for k,v in answers.iteritems():
                    
                    # Unsupported key
                    if not k in default_keys:
                        self.fb.warn('[init][db]: Unsupported environment variable: {0}'.format(k))
                    
                    # Set the environment variable
                    environ[k] = v
                    self.fb.success('[init][db]: Set environment variable: {0}'.format(env_var))
            
            # Get connection attributes prior to bootstrapping
            for k,a in prompts.iteritems():
                if not environ.get(k, None):
                    self.fb.input(a['prompt'], a['key'], **a.get('kwargs', {}))
                    environ[var_key] == self.fb.get_response(a['key'])
          
    def _init_map(self):
        """
        Map initialization keys to methods.
        
        :rtype: dict
        """
        return {
            'db': self._init_db
        }
          
    def get_answers(self):
        """
        Parse and return user-defined answers file.
        
        :rtype: dict
        """
        answers  = BootstrapAnswers(self.args.get('answers', None)).read()
        defaults = json_loads(open('{0}/defaults/answers.json'.format(LENSE_SHARE), 'r').read())
            
        # If user defined file
        if answers:
            _answers = merge_dict(defaults, answers)
            
            # Initialize
            if 'init' in _answers:
                for k,m in self._init_map().iteritems():
                    m(_answers['init'][k])
        return None
            
    def _run(self):
        """
        Private method for starting up the bootstrap process.
        """
        
        # Get command line arguments / answers
        self.args    = BootstrapArgs()
        self.answers = self.get_answers()
        
        # Set the Django settings module
        environ['DJANGO_SETTINGS_MODULE'] = 'lense.bootstrap.settings'
        
        # Setup Django for the bootstrap run
        django_setup()
            
        # Register project commons
        init_project('BOOTSTRAP', 'BOOTSTRAP')
        init_project('ENGINE', 'LENSE')
        
        # Show bootstrap information
        self.bootstrap_info()
        
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