import os
import sys
import json
import shutil
import django
import MySQLdb
from subprocess import Popen
from getpass import getpass
from feedback import Feedback

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'lense.engine.api.core.settings'

# Lense Libraries
from lense import PKG_ROOT
from lense.common.vars import LOG_DIR
import lense.common.logger as logger
import lense.common.config as config
from lense.common.cparse import CParse
from lense.common.bootstrap.params import BootstrapParams

try:
    from lense.engine.api.base import APIBare
except:
    pass

class Bootstrap(object):
    """
    Main class object for bootstrapping the Lense installation. This
    includes setting up the database and setting the admin user account.
    """
    def __init__(self):
        self.feedback = Feedback()
    
        # Configuration / logger
        self.conf   = config.parse()
        self.log    = logger.create('bootstrap', '{}/bootstrap.log'.format(LOG_DIR))
    
        # Bootstrap parameters
        self.params = BootstrapParams()
    
        # Server configuration file
        self.server_conf = self.params.file['config']['server_conf'][1]
        
        # Database connection
        self._connection = None
    
    def _die(self, msg):
        """
        Quit the program
        """
        self.log.error(msg)
        self.feedback.set(msg).error()
        sys.exit(1)
    
    def _deploy_config(self):
        """
        Deploy configuration files.
        """
        for f,p in self.params.file['config'].iteritems():
            if not os.path.isfile(p[1]):
                
                # Read the default file content
                c_file = open(p[0], 'r')
                c_str  = c_file.read()
                c_file.close()
                
                # Create the new configuration file
                d_file = open(p[1], 'w')
                d_file.write(c_str)
                d_file.close()
                
                # File deployed
                self.feedback.set('File <{}> deployed'.format(p[1])).success()
            else:
                self.feedback.set('File <{}> already deployed, skipping...'.format(p[1])).info()
    
        # Create the log and run directories
        for _dir in ['log', 'run']:
            dir = '{}/{}'.format(PKG_ROOT, _dir)
            if not os.path.isdir(dir):
                os.mkdir(dir)
                self.feedback.set('Created directory "{}"'.format(dir))
            else:
                self.feedback.set('Directory "{}" already exists, skipping...'.format(dir))
    
    def _get_password(self, prompt, min_length=8):
        _pass = getpass(prompt)
        
        # Make sure the password is long enough
        if not len(_pass) >= min_length:
            self.feedback.set('Password cannot be empty and must be at least {} characters long'.format(str(min_length))).error()
            return self._get_password(prompt, min_length)
            
        # Confirm the password
        _pass_confirm = getpass('Please confirm the password: ')
            
        # Make sure the passwords match
        if not _pass == _pass_confirm:
            self.feedback.set('Passwords do not match, try again').error()
            return self._get_password(prompt, min_length)
        return _pass
    
    def _get_input(self, prompt, default=None):
        _input = raw_input(prompt) or default
        
        # If no input found
        if not _input:
            self.feedback.set('Must provide a value').error()
            return self._get_input(prompt, default)
        return _input
    
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
            self.feedback.set('Connected to MySQL using root user').success()
        except Exception as e:
            self._die('Unable to connect to MySQL with root user: {}'.format(str(e)))
    
    def _bootstrap_complete(self):
        """
        Brief summary of the completed bootstrap process.
        """
        
        # Portal address
        portal_addr = 'http://{}:{}/'.format(
            self.params.input.response.get('portal_host'),
            self.params.input.response.get('portal_port')
        )
        
        # Print the summary
        self.feedback.set([
            'Lense bootstrap complete!',
            'To start all Lense processes, run "lense-server start".',
            'You may access the portal (if configured) using the "lense"'
            'user with the password created during the bootstrap process'
            'at: {}'.format(portal_addr)
        ]).block('COMPLETE')
        sys.exit(0)
    
    def _bootstrap_info(self):
        """
        Show a brief introduction and summary on the bootstrapping process.
        """
        self.feedback.set([
            'Lense Bootstrap Utility',
            'The bootstrap utility is used to get a new Lense installation up and',
            'running as quickly as possible. This will set up the database, make sure',
            'any required users exists, and populate the tables with seed data.'   
        ]).block('ABOUT')
    
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
            return self.feedback.set('Database encryption key/meta properties already exist').warn()
        
        # Generate the encryption key
        p_keycreate = Popen(['keyczart', 'create', '--location={}'.format(enc_attrs['dir']), '--purpose=crypt'])
        p_keycreate.communicate()
        if not p_keycreate.returncode == 0:
            return self.feedback.set('Failed to create database encryption key').error()
        self.feedback.set('Created database encryption key').success()
    
        # Add the encryption key
        p_keyadd = Popen(['keyczart', 'addkey', '--location={}'.format(enc_attrs['dir']), '--status=primary', '--size=256'])
        p_keyadd.communicate()
        if not p_keyadd.returncode == 0:
            return self.feedback.set('Failed to add database encryption key').error()
        self.feedback.set('Added database encryption key').success()
    
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
        self.log.info('Received response from <{}>: {}'.format(str(obj), json.dumps(group)))
        
        # If the group was not created
        if not group['valid']:
            self._die('HTTP {}: {}'.format(group['code'], group['content']))
        self.feedback.set('Created default Lense administrator group').success()
        
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
            self._die('HTTP {}: {}'.format(user['code'], user['content']))
        self.feedback.set('Created default Lense administrator account').success()
    
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
            
            # Store the utility UUID
            _util['uuid'] = util['data']['uuid']
            
            # If the utility was not created
            if not util['valid']:
                self._die('HTTP {}: {}'.format(util['code'], util['content']))
            self.feedback.set('Created database entry for utility "{}": Path={}, Method={}'.format(_util['cls'], _util['path'], _util['method'])).success()
    
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
                self._die('HTTP {}: {}'.format(acl_key['code'], acl_key['content']))
                
            # Store the new ACL key UUID
            _acl_key['uuid'] = acl_key['data']['uuid']
            self.feedback.set('Created database entry for ACL key "{}"'.format(_acl_key['name'])).success()
            
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
                    self.feedback.set('Granted global access to utility "{}" with ACL "{}"'.format(u, k['name'])).success()
    
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
            self.feedback.set('Created database entry for ACL object "{}->{}"'.format(_acl_obj['type'], _acl_obj['name'])).success()
    
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
                self.feedback.set('Granted global administrator access for ACL "{}"'.format(access['acl_name'])).success()
            except Exception as e:
                self._die('Failed to grant global access for ACL "{}": {}'.format(access['acl_name'], str(e)))
    
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
    
        # Update administrator info in the server configuration
        cp = CParse()
        cp.select(self.server_conf)
        cp.set_key('user', user['data']['username'], s='admin')
        cp.set_key('group', self.params.user['group'], s='admin')
        cp.set_key('key', user['data']['api_key'], s='admin')
        cp.apply()
        self.feedback.set('[{}] Set API administrator values'.format(self.server_conf)).success()
    
        # Create API utilities / ACL objects / ACL keys / access entries
        self._create_utils(GatewayUtilitiesCreate)
        self._create_acl_keys(GatewayACLCreate)
        self._create_utils_access(DBGatewayACLAccessGlobal, DBGatewayACLKeys, DBGatewayUtilities)
        self._create_acl_objects(GatewayACLObjectsCreate)
        self._create_acl_access(DBGatewayACLGroupGlobalPermissions, DBGatewayACLKeys, DBGroupDetails)
    
    def _read_input(self):
        """
        Read any required user input prompts
        """
        
        # Process each configuration section
        for section, obj in self.params.input.prompt.iteritems():
            print obj['label']
            print '-' * 20
        
            # Process each section input
            for key, attrs in obj['attrs'].iteritems():
                
                # Regular string input
                if attrs['type'] == 'str':
                    val = self._get_input(attrs['prompt'], attrs['default'])
                    
                # Password input
                if attrs['type'] == 'pass':
                    val = self._get_password(attrs['prompt'])
            
            
                # Store in response object
                self.params.input.set_response(key, val)
            print ''
        
        # Update and set database bootstrap attributes
        self.params.set_db()
    
    def _database(self):
        """
        Bootstrap the database and create all required tables and entries.
        """
            
        # Test the database connection
        self._try_mysql_root()
            
        # Create the database and user account
        try:
            _cursor = self._connection.cursor()
            
            # Create the database
            _cursor.execute(self.params.db['query']['create_db'])
            self.feedback.set('Created database "{}"'.format(self.params.db['attrs']['name'])).success()
            
            # Create the database user
            _cursor.execute(self.params.db['query']['create_user'])
            _cursor.execute(self.params.db['query']['grant_user'])
            _cursor.execute(self.params.db['query']['flush_priv'])
            self.feedback.set('Created database user "{}" with grants'.format(self.params.db['attrs']['user'])).success()
            
        except Exception as e:
            self._die('Failed to bootstrap Lense database: {}'.format(str(e)))
            
        # Close the connection
        _cursor.close()
        
        # Run Django syncdb
        try:
            app  = '{}/engine/api/manage.py'.format(PKG_ROOT)
            proc = Popen(['python', app, 'migrate'])
            proc.communicate()
            
            # Make sure the command ran successfully
            if not proc.returncode == 0:
                self._die('Failed to sync Django application database')
                
            # Sync success
            self.feedback.set('Synced Django application database').success()
        except Exception as e:
            self._die('Failed to sync Django application database: {}'.format(str(e)))
            
        # Set up database encryption
        self._database_encryption()
            
        # Set up the database seed data
        self._database_seed()
         
    def _update_config(self):
        """
        Update the deployed default server configuration.
        """
        
        # Parse and update the configuration
        cp = CParse()
        cp.select(self.server_conf)
        
        # Update each section
        for section, pair in self.params.get_config().iteritems():
            for key, val in pair.iteritems():
                cp.set_key(key, val, s=section)
                
                # Format the value output
                self.feedback.set('[{}] Set key value for "{}->{}"'.format(self.server_conf, section, key)).success()
            
        # Apply the configuration changes
        cp.apply()
        self.feedback.set('Applied updated server configuration').success()
            
    def run(self):
        """
        Kickstart the bootstrap process for Lense.
        """
        
        # Show bootstrap information
        self._bootstrap_info()
        
        # Read user input
        self._read_input()
        
        # Bootstrap the configuration files and update
        self._deploy_config()
        self._update_config()
        
        # Bootstrap the database
        self._database()
        
        # Bootstrap complete
        self._bootstrap_complete()