from time import time
from os import environ
from collections import OrderedDict
from json import loads as json_loads

# Django Libraries
from django import setup as django_setup

# Lense Libraries
from lense import import_class
from lense.common.vars import SHARE
from lense.common import init_project
from lense.bootstrap.common import BootstrapCommon

class Bootstrap(BootstrapCommon):
    """
    Main class object for bootstrapping the Lense installation. This
    includes setting up the database and the admin user account.
    """
    def __init__(self):
        super(Bootstrap, self).__init__('bootstrap')
            
        # Internal feedback / arguments / answers objects
        self._feedback = import_class('Feedback', 'feedback')
        self._args     = import_class('BootstrapArgs', 'lense.bootstrap.args')
        self._answers  = import_class('BootstrapAnswers', 'lense.bootstrap.answers', init=False).get(file=self._args.get('answers', None))
            
        # Bootstrap initialization
        self._bootstrap_init('db')
            
    def _bootstrap_init(self, key):
        """
        Wrapper for bootstrap initialization methods.
        
        :param key: The initialization method to run
        :type  key: str
        """
        if not 'init' in self._answers: return
        
        # Init keys
        init_keys = {'db': self._bootstrap_db}
        
        # Init key not found
        if not key in init_keys: return
        
        # Run the init method
        init_keys[key](self._answers['init'][key])
        
        # Delete init answers
        del self._answers['init'][key]
            
        # If last key
        if not self._answers['init']:
            del self._answers['init']
            
    def _bootstrap_engine(self):
        """
        Helper method to see if we are bootstrapping the Lense Engine, which
        requires database connection settings.
        """
        
        # Explicity bootstrapping Engine
        if self._args.get('engine'):
            return True
            
        # Bootstrapping all
        bootstrap_all = True
        for k in ['engine', 'client', 'portal', 'socket']:
            if self._args.get(k, False):
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
            self._feedback.info('Running bootstrap manager for Lense project: {0}'.format(project))
            import_class(project_cls, 'lense.bootstrap.projects').run()
          
    def _bootstrap_db(self, answers):
        """
        Bootstrap database settings.
        """
        default_answers = json_loads(open('{0}/defaults/answers.json'.format(SHARE.BOOTSTRAP), 'r').read())
        default_keys = default_answers['init']['db']
        
        # Bootstrapping the engine requires a database connection
        if self._bootstrap_engine():
            self._feedback.info('[init][db] Initializing database')
            prompts = json_loads(open('{0}/prompts/init/database.json'.format(SHARE.BOOTSTRAP), 'r').read())
            
            # Answers supplied
            if answers:
                for k,v in answers.iteritems():
                    
                    # Unsupported key
                    if not k in default_keys:
                        self._feedback.warn('[init][db] Unsupported environment variable: {0}'.format(k))
                    
                    # Set the environment variable
                    environ[k] = v
                    self._feedback.success('[init][db] Set environment variable: {0}'.format(k))
            
            # Get connection attributes prior to bootstrapping
            for k,a in prompts.iteritems():
                if not environ.get(k, None):
                    self._feedback.input(a['prompt'], a['key'], **a.get('kwargs', {}))
                    environ[var_key] == self._feedback.get_response(a['key'])
            
    def _run(self):
        """
        Private method for starting up the bootstrap process.
        """
        
        # Start time
        start = time()
        
        # Set the Django settings module
        environ['DJANGO_SETTINGS_MODULE'] = 'lense.bootstrap.settings'
        
        # Setup Django for the bootstrap run
        django_setup()
            
        # Register project commons
        init_project('BOOTSTRAP', 'BOOTSTRAP')
        init_project('ENGINE', 'LENSE')
        
        # Store arguments / answers
        BOOTSTRAP.ARGS    = self._args
        BOOTSTRAP.ANSWERS = self._answers
        
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
            
        # Finished
        BOOTSTRAP.FEEDBACK.info('Finished bootstrapping in: {0} seconds'.format(str(time() - start)))
            
    @classmethod
    def run(cls):
        """
        Public class method for invoking the bootstrap manager.
        """
        
        # Set the bootstrap environment variable
        environ['BOOTSTRAP'] = '0'
        
        # Run the bootstrap manager
        return cls()._run()