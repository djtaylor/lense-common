import os
import sys
import json
import shutil
import django
import MySQLdb
import argparse
from subprocess import Popen, PIPE
from getpass import getpass
from feedback import Feedback

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'lense.engine.api.core.settings'

# Lense Libraries
from lense.common.vars import LOG_DIR, RUN_DIR, WSGI_CONFIG, LENSE_CONFIG
import lense.common.logger as logger
from lense.common.config import LenseConfigEditor
from lense.common.objects import JSONObject
from lense.common.bootstrap.engine_params import EngineParams
from lense.common.bootstrap.portal_params import PortalParams

try:
    from lense.engine.api.base import APIBare
except:
    pass

class _BootstrapArgs(object):
    """
    Class object for handling arguments passed to the bootstrap manager.
    """
    def __init__(self):
        
        # Arguments parser / object
        self.parser  = None
        self._args   = None
        
        # Construct arguments
        self._construct()
        
    def list(self):
        """
        Return a list of argument keys.
        """
        return self._args.keys()
        
    def _return_help(self):
         return ("Lense Bootstrap Manager\n\n"
                 "A utility designed to handle bootstrapping a Lense installation. The\n"
                 "default action is to bootstrap all projects unless otherwise specified\n"
                 "with arguments.")
        
    def _construct(self):
        """
        Construct the argument parser.
        """
        
        # Create a new argument parsing object and populate the arguments
        self.parser = argparse.ArgumentParser(description=self._return_help(), formatter_class=argparse.RawTextHelpFormatter)
        self.parser.add_argument('-e', '--engine', help='Bootstrap the Lense API engine', action='store_true')
        self.parser.add_argument('-p', '--portal', help='Bootstrap the Lense API portal', action='store_true')
      
        # Parse CLI arguments
        sys.argv.pop(0)
        self._args = vars(self.parser.parse_args(sys.argv))
        
    def set(self, k, v):
        """
        Set a new argument or change the value.
        """
        self._args[k] = v
        
    def get(self, k, default=None, use_json=False):
        """
        Retrieve an argument passed via the command line.
        """
        
        # Get the value from argparse
        _raw = self._args.get(k)
        _val = (_raw if _raw else default) if not isinstance(_raw, list) else (_raw[0] if _raw[0] else default)
        
        # Return the value
        return _val if not use_json else json.dumps(_val)

class _BootstrapCommon(object):
    """
    Common class object for bootstrap handlers.
    """
    def __init__(self):
        
        # Feedback
        self.feedback = Feedback()
        
        # Make sure being run as root
        self._check_root()
        
        # Logger
        self.log      = logger.create('bootstrap', '{0}/bootstrap.log'.format(LOG_DIR))

    def _check_root(self):
        """
        Bootstrap manager needs to be run as root.
        """
        if not os.geteuid() == 0:
            self._die('Lense bootstrap manager must be run with root privileges', log=False)

    def _die(self, msg, log=True):
        """
        Quit the program
        """
        
        # Log the message unless explicitly specified otherwise
        if log:
            self.log.error(msg)
            
        # Show the error and quit
        self.feedback.error(msg)
        sys.exit(1)

    def _deploy_apache(self, project):
        """
        Deploy Apache configuration files.
        """
        
        # Project configurations
        _project_config = {
            'engine': WSGI_CONFIG.ENGINE[0],
            'portal': WSGI_CONFIG.PORTAL[0]
        }
    
        # Enable the site configuration
        proc = Popen(['a2ensite', _project_config[project]], stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        
        # Make sure the command returned successfully
        if not proc.returncode == 0:
            self._die('Failed to enable virtual host: {0}'.format(str(err)))
        self.feedback.success('Enabled virtual host configuration for Lense API {0}'.format(project))

    def _mkdirs(self, _dirs):
        """
        Make required directories.
        """
    
        # Create the log and run directories
        for _dir in _dirs:
            if not os.path.isdir(_dir):
                os.mkdir(_dir)
                self.feedback.info('Created directory "{0}"'.format(_dir))
            else:
                self.feedback.info('Directory "{0}" already exists, skipping...'.format(_dir))

    def _get_password(self, prompt, min_length=8):
        _pass = getpass(prompt)
        
        # Make sure the password is long enough
        if not len(_pass) >= min_length:
            self.feedback.error('Password cannot be empty and must be at least {0} characters long'.format(str(min_length)))
            return self._get_password(prompt, min_length)
            
        # Confirm the password
        _pass_confirm = getpass('Please confirm the password: ')
            
        # Make sure the passwords match
        if not _pass == _pass_confirm:
            self.feedback.error('Passwords do not match, try again')
            return self._get_password(prompt, min_length)
        return _pass

    def _get_input(self, prompt, default=None):
        _input = raw_input(prompt) or default
        
        # If no input found
        if not _input:
            self.feedback.error('Must provide a value')
            return self._get_input(prompt, default)
        return _input
    
    def _read_input(self, answer_file):
        """
        Read any required user input prompts
        """
        
        # Look for an answer file
        try:
            afile = JSONObject()
            answers = afile.from_file(answer_file)
        except:
            answers = {}
        
        # Process each configuration section
        for section, obj in self.params.input.prompt.iteritems():
            print obj['label']
            print '-' * 20
        
            # Process each section input
            for key, attrs in obj['attrs'].iteritems():
                
                # If an answer already defined
                if key in answers:
                    self.feedback.info('Value for {0} found in answer file'.format(key))
                    val = answers[key]
                    
                else:
                
                    # Regular string input
                    if attrs['type'] == 'str':
                        val = self._get_input(attrs['prompt'], attrs['default'])
                        
                    # Password input
                    if attrs['type'] == 'pass':
                        val = self._get_password(attrs['prompt'])
            
                # Store in response object
                self.params.input.set_response(key, val)
            print ''
    
    def _update_config(self, project):
        """
        Update the deployed default server configuration.
        """
        
        # Parse and update the configuration
        lce = LenseConfigEditor(project.upper())
        
        # Update each section
        for section, pair in self.params.get_config().iteritems():
            for key, val in pair.iteritems():
                lce.set('{0}/{1}'.format(section, key), val)
            
                # Format the value output
                self.feedback.success('[{0}] Set key value for "{1}->{2}"'.format(getattr(LENSE_CONFIG, project.upper()), section, key))
            
        # Apply the configuration changes
        lce.save()
        self.feedback.success('Applied updated {0} configuration'.format(project))
    
    def _bootstrap_info(self):
        """
        Show a brief introduction and summary on the bootstrapping process.
        """
        self.feedback.block([
            'Lense Bootstrap Utility',
            'The bootstrap utility is used to get a new Lense installation up and',
            'running as quickly as possible. This will set up the database, make sure',
            'any required users exists, and populate the tables with seed data.'   
        ], 'ABOUT')

class _BootstrapEngine(_BootstrapCommon):
    """
    Class object for handling bootstrap of the Lense API engine.
    """
    def __init__(self):
        super(_BootstrapEngine, self).__init__()
        
        # Bootstrap parameters
        self.params   = EngineParams()
        
        # Database connection
        self._connection = None
        
    def _try_mysql_root(self):
        """
        Attempt to connect to the MySQL server as root user.
        """
        try:
            self._connection = MySQLdb.connect(
                host   = self.params.input.response.get('db_host'), 
                port   = int(self.params.input.response.get('db_port')),
                user   = 'root',
                passwd = self.params.input.response.get('db_root_password')
            )
            self.feedback.success('Connected to MySQL using root user')
        except Exception as e:
            self._die('Unable to connect to MySQL with root user: {0}'.format(str(e)))
    
    def _keyczart_create(self, enc_attrs):
        """
        Create a new database encryption key.
        """
        p_keycreate = Popen(['keyczart', 'create', '--location={0}'.format(enc_attrs['dir']), '--purpose=crypt'])
        p_keycreate.communicate()
        
        # Failed to generate key
        if not p_keycreate.returncode == 0:
            self.feedback.error('Failed to create database encryption key')
            return False
        
        # Generated encryption key
        self.feedback.success('Created database encryption key')
        return True
    
    def _keyczart_add(self, enc_attrs):
        """
        Add a bew database encryption key.
        """
        p_keyadd = Popen(['keyczart', 'addkey', '--location={0}'.format(enc_attrs['dir']), '--status=primary', '--size=256'])
        p_keyadd.communicate()
        
        # Failed to add key
        if not p_keyadd.returncode == 0:
            self.feedback.error('Failed to add database encryption key')
            return False
        
        # Added key
        self.feedback.success('Added database encryption key')
        return True
    
    def _database_encryption(self):
        """
        Bootstrap the database encryption keys.
        """
        
        # Encryption attributes
        enc_attrs = {
            'key': self.params.db['attrs']['encryption']['key'],
            'meta': self.params.db['attrs']['encryption']['meta'],
            'dir': self.params.db['attrs']['encryption']['dir']
        }
        
        # Make sure neither file exists
        if os.path.isfile(enc_attrs['key']) or os.path.isfile(enc_attrs['meta']):
            return self.feedback.warn('Database encryption key/meta properties already exist')
        
        # Generate / add encryption key
        for m in [self._keyczart_create, self._keyczart_add]:
            if not m(enc_attrs):
                return False
    
    def _create_group(self, obj):
        """
        Create the default administrator group.
        """
        group = obj(APIBare(
            data = {
                'uuid': self.params.group['uuid'],
                'name': self.params.group['name'],
                'desc': self.params.group['desc'],
                'protected': self.params.group['protected']
            },
            path = 'group'
        )).launch()
        self.log.info('Received response from <{0}>: {1}'.format(str(obj), json.dumps(group)))
        
        # If the group was not created
        if not group['valid']:
            self._die('HTTP {0}: {1}'.format(group['code'], group['content']))
        self.feedback.success('Created default Lense administrator group')
        
        # Return the group object
        return group
    
    def _create_user(self, obj):
        """
        Create the default administrator user account.
        """
        
        # Set the new user email/password
        user_email = self.params.input.response.get('api_admin_email', self.params.user['email'])
        user_passwd = self.params.input.response.get('api_admin_password', self.params.user['password'])
        
        # Create a new user object
        user = obj(APIBare(
            data = {
                'username': self.params.user['username'],
                'group': self.params.user['group'],
                'email': user_email,
                'password': user_passwd,
                'password_confirm': user_passwd
            },
            path = 'user'             
        )).launch()
        self.log.info('Received response from <{}>: {}'.format(str(obj), json.dumps(user)))
        
        # If the user was not created
        if not user['valid']:
            self._die('HTTP {0}: {1}'.format(user['code'], user['content']))
        self.feedback.success('Created default Lense administrator account')
    
        # Return the user object
        return user
    
    def _create_utils(self, obj):
        """
        Create API utility entries.
        """
        for _util in self.params.utils:
            util = obj(APIBare(
                data = {
                    'path': _util['path'],
                    'desc': _util['desc'],
                    'method': _util['method'],
                    'mod': _util['mod'],
                    'cls': _util['cls'],
                    'protected': _util['protected'],
                    'enabled': _util['enabled'],
                    'object': _util['object'],
                    'object_key': _util['object_key'],
                    'rmap': json.dumps(_util['rmap'])
                },
                path = 'utilities'
            )).launch()
            
            # If the utility was not created
            if not util['valid']:
                self._die('HTTP {0}: {1}'.format(util['code'], util['content']))
            
            # Store the utility UUID
            _util['uuid'] = util['data']['uuid']
            self.feedback.success('Created database entry for utility "{0}": Path={1}, Method={2}'.format(_util['cls'], _util['path'], _util['method']))
    
    def _create_acl_keys(self, obj):
        """
        Create ACL key definitions.
        """
        for _acl_key in self.params.acl.keys:
            acl_key = obj(APIBare(
                data = {
                    "name": _acl_key['name'],
                    "desc": _acl_key['desc'],
                    "type_object": _acl_key['type_object'],
                    "type_global": _acl_key['type_global']
                },
                path = 'gateway/acl/objects'
            )).launch()
            
            # If the ACL key was not created
            if not acl_key['valid']:
                self._die('HTTP {0}: {1}'.format(acl_key['code'], acl_key['content']))
                
            # Store the new ACL key UUID
            _acl_key['uuid'] = acl_key['data']['uuid']
            self.feedback.success('Created database entry for ACL key "{0}"'.format(_acl_key['name']))
            
        # Setup ACL objects
        self.params.acl.set_objects()
    
    def _create_utils_access(self, g_access, key, util):
        """
        Permit access to utilities by ACL key.
        
        @param g_access: Global ACL access model
        @type  g_access: DBGatewayACLAccessGlobal
        @param key:      ACL key database model
        @type  key:      DBGatewayACLKeys
        @param util:     Utility database model
        @type  util:     DBGatewayUtilities
        """
        
        # Process ACL keys
        for k in self.params.acl.keys:
            if k['type_global']:
                for u in k['util_classes']:
                    g_access.objects.create(
                        acl = key.objects.get(uuid=k['uuid']),
                        utility = util.objects.get(cls=u)
                    ).save()
                    self.feedback.success('Granted global access to utility "{0}" with ACL "{1}"'.format(u, k['name']))
    
    def _create_acl_objects(self, obj):
        """
        Create ACL object definitions.
        """
        for _acl_obj in self.params.acl.objects:
            acl_obj = obj(APIBare(
                data = {
                    "type": _acl_obj['type'],
                    "name": _acl_obj['name'],
                    "acl_mod": _acl_obj['acl_mod'],
                    "acl_cls": _acl_obj['acl_cls'],
                    "acl_key": _acl_obj['acl_key'],
                    "obj_mod": _acl_obj['obj_mod'],
                    "obj_cls": _acl_obj['obj_cls'],
                    "obj_key": _acl_obj['obj_key'],
                    "def_acl": _acl_obj['def_acl']
                },
                path = 'gateway/acl/objects'
            )).launch()
            
            # If the ACL object was not created
            if not acl_obj['valid']:
                self._die('HTTP {}: {}'.format(acl_obj['code'], acl_obj['content']))
            self.feedback.success('Created database entry for ACL object "{0}->{1}"'.format(_acl_obj['type'], _acl_obj['name']))
    
    def _create_acl_access(self, obj, keys, groups):
        """
        Setup ACL group access definitions.
        """
        for access in self.params.acl.set_access(self.params.acl.keys):
            try:
                obj.objects.create(
                    acl = keys.objects.get(uuid=access['acl']),
                    owner = groups.objects.get(uuid=access['owner']),
                    allowed = access['allowed']
                ).save()
                self.feedback.success('Granted global administrator access for ACL "{0}"'.format(access['acl_name']))
            except Exception as e:
                self._die('Failed to grant global access for ACL "{0}": {1}'.format(access['acl_name'], str(e)))
    
    def _database_seed(self):
        """
        Seed the database with the base information needed to run Lense.
        """
        
        # Import modules now to get the new configuration
        from lense.engine.api.app.group.utils import GroupCreate
        from lense.engine.api.app.user.utils import UserCreate
        from lense.engine.api.app.group.models import DBGroupDetails
        from lense.engine.api.app.gateway.models import DBGatewayACLGroupGlobalPermissions, DBGatewayACLKeys, \
                                                             DBGatewayACLAccessGlobal, DBGatewayUtilities
        from lense.engine.api.app.gateway.utils import GatewayUtilitiesCreate, GatewayACLObjectsCreate, \
                                                            GatewayACLCreate
        
        # Setup Django models
        django.setup()
        
        # Create the administrator group and user
        group = self._create_group(GroupCreate)
        user = self._create_user(UserCreate)
    
        # Store the new username and API key
        self.params.user['username'] = user['data']['username']
        self.params.user['key'] = user['data']['api_key']
    
        # Update administrator info in the server configuration
        lce = LenseConfigEditor('ENGINE')
        lce.set('admin/user', user['data']['username'])
        lce.set('admin/group', self.params.user['group'])
        lce.set('admin/key', user['data']['api_key'])
        lce.save()
        self.feedback.success('[{0}] Set API administrator values'.format(LENSE_CONFIG.ENGINE))
    
        # Create API utilities / ACL objects / ACL keys / access entries
        self._create_utils(GatewayUtilitiesCreate)
        self._create_acl_keys(GatewayACLCreate)
        self._create_utils_access(DBGatewayACLAccessGlobal, DBGatewayACLKeys, DBGatewayUtilities)
        self._create_acl_objects(GatewayACLObjectsCreate)
        self._create_acl_access(DBGatewayACLGroupGlobalPermissions, DBGatewayACLKeys, DBGroupDetails)
    
    def _database(self):
        """
        Bootstrap the database and create all required tables and entries.
        """
            
        # Set database attributes
        self.params.set_db()
            
        # Test the database connection
        self._try_mysql_root()
            
        # Create the database and user account
        try:
            _cursor = self._connection.cursor()
            
            # Create the database
            _cursor.execute(self.params.db['query']['create_db'])
            self.feedback.success('Created database "{0}"'.format(self.params.db['attrs']['name']))
            
            # Create the database user
            _cursor.execute(self.params.db['query']['create_user'])
            _cursor.execute(self.params.db['query']['grant_user'])
            _cursor.execute(self.params.db['query']['flush_priv'])
            self.feedback.success('Created database user "{0}" with grants'.format(self.params.db['attrs']['user']))
            
        except Exception as e:
            self._die('Failed to bootstrap Lense database: {0}'.format(str(e)))
            
        # Close the connection
        _cursor.close()
        
        # Run Django syncdb
        try:
            app  = '/usr/lib/python2.7/dist-packages/lense/engine/api/manage.py'
            proc = Popen(['python', app, 'migrate'])
            proc.communicate()
            
            # Make sure the command ran successfully
            if not proc.returncode == 0:
                self._die('Failed to sync Django application database')
                
            # Sync success
            self.feedback.success('Synced Django application database')
        except Exception as e:
            self._die('Failed to sync Django application database: {0}'.format(str(e)))
            
        # Set up database encryption
        self._database_encryption()
            
        # Set up the database seed data
        self._database_seed()
        
    def _bootstrap_complete(self):
        """
        Brief summary of the completed bootstrap process.
        """
        
        # Print the summary
        self.feedback.block([
            'Finished bootstrapping Lense API engine!\n',
            'You should restart your Apache service to load the new virtual host',
            'configuration. In order to use the Lense CLI client you should add the',
            'following environment variables to your ~/.bashrc file:\n',
            'export LENSE_API_USER = "{0}"'.format(self.params.user['username']),
            'export LENSE_API_KEY = "{0}"'.format(self.params.user['group']),
            'export LENSE_API_GROUP = "{0}"'.format(self.params.user['key'])  
        ], 'COMPLETE')
        
class _BootstrapPortal(_BootstrapCommon):
    """
    Class object for handling bootstrap of the Lense API portal.
    """
    def __init__(self):
        super(_BootstrapPortal, self).__init__()

        # Bootstrap parameters
        self.params   = PortalParams()

    def _bootstrap_complete(self):
        """
        Brief summary of the completed bootstrap process.
        """
        
        # Print the summary
        self.feedback.block([
            'Finished bootstrapping Lense API portal!\n',
            'You should restart your Apache service to load the new virtual host',
            'configuration. You can connect to the Lense API portal using the',
            'administrator credentials generated during the engine bootstrap process',
            'at the following URL:\n',
            'http://{0}:{1}'.format(self.params.input.response.get('portal_host'), self.params.input.response.get('portal_port'))
        ], 'COMPLETE')

class Bootstrap(_BootstrapCommon):
    """
    Main class object for bootstrapping the Lense installation. This
    includes setting up the database and the admin user account.
    """
    def __init__(self):
        super(Bootstrap, self).__init__()
    
        # Arguments
        self.args = _BootstrapArgs()
    
    def _bootstrap_engine(self):
        """        
        Bootstrap the Lense API engine.
        """
        _handler = _BootstrapEngine()
            
        # Get user input
        _handler._read_input('/tmp/lense_engine_bootstrap.js')
        
        # Create required directories and update the configuration
        _handler._mkdirs([LOG_DIR, RUN_DIR])
        _handler._update_config('engine')
            
        # Deploy the Apache configuration
        _handler._deploy_apache('engine')
        
        # Bootstrap the database
        _handler._database()
        
        # Show to bootstrap complete summary
        _handler._bootstrap_complete()
            
    def _bootstrap_portal(self):
        """
        Bootstrap the Lense API portal.
        """
        _handler = _BootstrapPortal()
            
        # Get user input
        _handler._read_input('/tmp/lense_portal_bootstrap.js')
        
        # Create required directories and update the configuration
        _handler._mkdirs([LOG_DIR])
            
        # Deploy the Apache configuration
        _handler._deploy_apache('portal')
            
        # Show to bootstrap complete summary
        _handler._bootstrap_complete()
            
    def _bootstrap_project(self, project):
        """
        Bootstrap a specific project.
        """
        _bootstrap_methods = {
            'engine': self._bootstrap_engine,
            'portal': self._bootstrap_portal
        }
        
        # Run the project bootstrap method
        if project in _bootstrap_methods:
            self.feedback.info('Running bootstrap manager for Lense API {0}...\n'.format(project))
            _bootstrap_methods[project]()
            
    def _bootstrap_all(self):
        """
        Bootstrap all projects.
        """
        self._bootstrap_project('engine')
        self._bootstrap_project('portal')
            
    def run(self):
        """
        Kickstart the bootstrap process for Lense.
        """
        
        # Show bootstrap information
        self._bootstrap_info()
        
        # Bootstrap projects
        _bootstrap = {
            'engine': self.args.get('engine', False),
            'portal': self.args.get('portal', False)
        }
        
        # If not bootstrapping a specific project
        if not _bootstrap['engine'] and not _bootstrap['portal']:
            self._bootstrap_all()
            
        # Bootstrapping specific projects
        else:
            for project, run_bootstrap in _bootstrap.iteritems():
                if run_bootstrap:
                    self._bootstrap_project(project)