from os import environ
from subprocess import Popen
from json import dumps as json_dumps
from MySQLdb import connect as mysql_connect

# Set the Django settings module
environ['DJANGO_SETTINGS_MODULE'] = 'lense.engine.api.core.settings'

# Lense Libraries
from lense.common import LenseCommon
from lense.common.vars import USERS, GROUPS
from lense.common.bootstrap.params import EngineParams
from lense.common.bootstrap.common import BootstrapCommon

# Lense Common
LENSE = LenseCommon('BOOTSTRAP')

class BootstrapEngine(BootstrapCommon):
    """
    Class object for handling bootstrap of the Lense API engine.
    """
    def __init__(self):
        super(BootstrapEngine, self).__init__('engine')
        
        # Bootstrap parameters
        self.params   = EngineParams()
        
        # Database connection
        self._connection = None
        
    def _try_mysql_root(self):
        """
        Attempt to connect to the MySQL server as root user.
        """
        try:
            self._connection = mysql_connect(
                host   = self.params.input.response.get('db_host'), 
                port   = int(self.params.input.response.get('db_port')),
                user   = 'root',
                passwd = self.params.input.response.get('db_root_password')
            )
            LENSE.FEEDBACK.success('Connected to MySQL using root user')
        except Exception as e:
            self.die('Unable to connect to MySQL with root user: {0}'.format(str(e)))
    
    def _keyczart_create(self, enc_attrs):
        """
        Create a new database encryption key.
        """
        proc = Popen(['keyczart', 'create', '--location={0}'.format(enc_attrs['dir']), '--purpose=crypt'])
        proc.communicate()
        
        # Failed to generate key
        if not proc.returncode == 0:
            LENSE.FEEDBACK.error('Failed to create database encryption key')
            return False
        
        # Generated encryption key
        LENSE.FEEDBACK.success('Created database encryption key')
        return True
    
    def _keyczart_add(self, enc_attrs):
        """
        Add a bew database encryption key.
        """
        proc = Popen(['keyczart', 'addkey', '--location={0}'.format(enc_attrs['dir']), '--status=primary', '--size=256'])
        proc.communicate()
        
        # Failed to add key
        if not proc.returncode == 0:
            LENSE.FEEDBACK.error('Failed to add database encryption key')
            return False
        
        # Added key
        LENSE.FEEDBACK.success('Added database encryption key')
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
            return LENSE.FEEDBACK.warn('Database encryption key/meta properties already exist')
        
        # Generate / add encryption key
        for m in [self._keyczart_create, self._keyczart_add]:
            if not m(enc_attrs):
                return False
    
    def _create_groups(self, obj):
        """
        Create the default administrator group.
        """
        
        # Groups container
        _groups = []
        
        # Create each new group
        for _g in self.params.groups:
            g = obj(APIBare(
                data = {
                    'uuid':      _g['uuid'],
                    'name':      _g['name'],
                    'desc':      _g['desc'],
                    'protected': _g['protected']
                },
                path = 'group'
            )).launch()
            LENSE.LOG.info('Received response from <{0}>: {1}'.format(str(obj), json_dumps(g)))
        
            # If the group was not created
            if not g['valid']:
                self.die('HTTP {0}: {1}'.format(g['code'], g['content']))
            LENSE.FEEDBACK.success('Created Lense group: {0}'.format(g['data']['name']))
        
        # Return the groups object
        return _groups
    
    def _create_users(self, obj):
        """
        Create the default administrator user account.
        """
        
        # Users container
        _users = []
        
        # Create each new user
        for user in self.params.users:
            _keys = user.get('_keys')
            
            # User password
            password = self.params.input.response.get(_keys['password'], rstring(12))
            
            # User data
            _data = {
                'username': user['username'],
                'group': user['group'],
                'email': self.params.input.response.get(_keys['email'], user['email']),
                'password': password,
                'password_confirm': password    
            }
            
            # Create a new user object
            user = obj(APIBare(data=_data, path='user')).launch()
            LENSE.LOG.info('Received response from <{0}>: {1}'.format(str(obj), json_dumps(user)))
            
            # If the user was not created
            if not user['valid']:
                self.die('HTTP {0}: {1}'.format(user['code'], user['content']))
            LENSE.FEEDBACK.success('Created Lense account: {0}'.format(_data['username']))
        
            # Add to the users object
            _users.append(user)
        
        # Return the user object
        return _users
    
    def _create_handlers(self, obj):
        """
        Create API handler entries.
        """
        for _h in self.params.handlers:
            h = obj(APIBare(
                data = {
                    'path':       _h['path'],
                    'name':       _h['name'],
                    'desc':       _h['desc'],
                    'method':     _h['method'],
                    'mod':        _h['mod'],
                    'cls':        _h['cls'],
                    'protected':  _h['protected'],
                    'enabled':    _h['enabled'],
                    'object':     _h['object'],
                    'object_key': _h['object_key'],
                    'allow_anon': _h.get('allow_anon', False),
                    'rmap':       json_dumps(_h['rmap'])
                },
                path = 'handler'
            )).launch()
            
            # If the handler was not created
            if not h['valid']:
                self.die('HTTP {0}: {1}'.format(h['code'], h['content']))
            
            # Store the handler UUID
            _h['uuid'] = h['data']['uuid']
            LENSE.FEEDBACK.success('Created database entry for handler "{0}": Path={1}, Method={2}'.format(_h['name'], _h['path'], _h['method']))
    
    def _create_acl_keys(self, obj):
        """
        Create ACL key definitions.
        """
        for _a in self.params.acl.keys:
            a = obj(APIBare(
                data = {
                    "name":        _a['name'],
                    "desc":        _a['desc'],
                    "type_object": _a['type_object'],
                    "type_global": _a['type_global']
                },
                path = 'gateway/acl/objects'
            )).launch()
            
            # If the ACL key was not created
            if not a['valid']:
                self.die('HTTP {0}: {1}'.format(a['code'], a['content']))
                
            # Store the new ACL key UUID
            _a['uuid'] = a['data']['uuid']
            LENSE.FEEDBACK.success('Created database entry for ACL key "{0}"'.format(_a['name']))
            
        # Setup ACL objects
        self.params.acl.set_objects()
    
    def _create_handlers_access(self, g_access, key, handler):
        """
        Permit access to handlers by ACL key.
        
        @param g_access: Global ACL access model
        @type  g_access: ACLGlobalAccess
        @param key:      ACL key database model
        @type  key:      ACLKeys
        @param handler:  Handler database model
        @type  handler:  Handlers
        """
        
        # Process ACL keys
        for k in self.params.acl.keys:
            if k['type_global']:
                for u in k['handler_classes']:
                    g_access.objects.create(
                        acl = key.objects.get(uuid=k['uuid']),
                        handler = handler.objects.get(cls=u)
                    ).save()
                    LENSE.FEEDBACK.success('Granted global access to handler "{0}" with ACL "{1}"'.format(u, k['name']))
    
    def _create_acl_objects(self, obj):
        """
        Create ACL object definitions.
        """
        for _a in self.params.acl.objects:
            a = obj(APIBare(
                data = {
                    "type": _a['type'],
                    "name": _a['name'],
                    "acl_mod": _a['acl_mod'],
                    "acl_cls": _a['acl_cls'],
                    "acl_key": _a['acl_key'],
                    "obj_mod": _a['obj_mod'],
                    "obj_cls": _a['obj_cls'],
                    "obj_key": _a['obj_key'],
                    "def_acl": _a['def_acl']
                },
                path = 'gateway/acl/objects'
            )).launch()
            
            # If the ACL object was not created
            if not a['valid']:
                self.die('HTTP {}: {}'.format(a['code'], a['content']))
            LENSE.FEEDBACK.success('Created database entry for ACL object "{0}->{1}"'.format(_a['type'], _a['name']))
    
    def _create_acl_access(self, obj, keys, groups):
        """
        Setup ACL group access definitions.
        """
        for a in self.params.acl.set_access(self.params.acl.keys):
            try:
                obj.objects.create(
                    acl = keys.objects.get(uuid=a['acl']),
                    owner = groups.objects.get(uuid=a['owner']),
                    allowed = a['allowed']
                ).save()
                LENSE.FEEDBACK.success('Granted global administrator access for ACL "{0}"'.format(a['acl_name']))
            except Exception as e:
                self.die('Failed to grant global access for ACL "{0}": {1}'.format(a['acl_name'], str(e)))
    
    def _database_seed(self):
        """
        Seed the database with the base information needed to run Lense.
        """
        
        # Request handlers
        from lense.engine.api.handlers.user import User_Create
        from lense.engine.api.handlers.group import Group_Create
        from lense.engine.api.handlers.handler import Handler_Create
        from lense.engine.api.handlers.acl import ACLObjects_Create, ACL_Create
        
        # Common object models
        from lense.common.objects.group.models import APIGroups
        from lense.common.objects.handler.models import Handlers
        from lense.common.objects.acl.models import ACLGroupPermissions_Global, ACLKeys, ACLGlobalAccess
        
        # Setup Django models
        django.setup()
        
        # Create the administrator group and user
        group = self._create_groups(Group_Create)
        users = self._create_users(User_Create)
    
        # Store the new username and API key
        for user in users:
            if not user['data']['username'] == USERS.ADMIN.NAME:
                continue
            
            # Get the user parameters
            user_params = self.params.get_user(USERS.ADMIN.NAME)
            
            # Default administrator
            self.params.set_user(USERS.ADMIN.NAME, 'key', user['data']['api_key'])
            self.params.set_user(USERS.ADMIN.NAME, 'username', user['data']['username'])
    
            # Update administrator info in the server configuration
            lce = LenseConfigEditor('ENGINE')
            lce.set('admin/user', user['data']['username'])
            lce.set('admin/group', user_params['group'])
            lce.set('admin/key', user['data']['api_key'])
            lce.save()
            LENSE.FEEDBACK.success('[{0}] Set API administrator values'.format(LENSE_CONFIG.ENGINE))
    
        # Create API handlers / ACL objects / ACL keys / access entries
        self._create_handlers(Handler_Create)
        self._create_acl_keys(ACL_Create)
        self._create_handlers_access(ACLGlobalAccess, ACLKeys, Handlers)
        self._create_acl_objects(ACLObjects_Create)
        self._create_acl_access(ACLGroupPermissions_Global, ACLKeys, APIGroups)
    
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
            c = self._connection.cursor()
            
            # Create the database
            c.execute(self.params.db['query']['create_db'])
            LENSE.FEEDBACK.success('Created database "{0}"'.format(self.params.db['attrs']['name']))
            
            # Create the database user
            c.execute(self.params.db['query']['create_user'])
            c.execute(self.params.db['query']['grant_user'])
            c.execute(self.params.db['query']['flush_priv'])
            LENSE.FEEDBACK.success('Created database user "{0}" with grants'.format(self.params.db['attrs']['user']))
            
        except Exception as e:
            self.die('Failed to bootstrap Lense database: {0}'.format(str(e)))
            
        # Close the connection
        c.close()
        
        # Set up database encryption
        self._database_encryption()
        
        # Run Django syncdb
        try:
            app  = '/usr/lib/python2.7/dist-packages/lense/engine/api/manage.py'
            proc = Popen(['python', app, 'migrate'])
            proc.communicate()
            
            # Make sure the command ran successfully
            if not proc.returncode == 0:
                self.die('Failed to sync Django application database')
                
            # Sync success
            LENSE.FEEDBACK.success('Synced Django application database')
        except Exception as e:
            self.die('Failed to sync Django application database: {0}'.format(str(e)))
            
        # Set up the database seed data
        self._database_seed()
        
    def _bootstrap_complete(self):
        """
        Brief summary of the completed bootstrap process.
        """
        
        # Get the admin user
        admin_user = self.params.get_user(USERS.ADMIN.NAME)
        
        # Print the summary
        LENSE.FEEDBACK.block([
            'Finished bootstrapping Lense API engine!\n',
            'You should restart your Apache service to load the new virtual host',
            'configuration. In order to use the Lense CLI client you should add the',
            'following environment variables to your ~/.bashrc file:\n',
            'export LENSE_API_USER="{0}"'.format(admin_user['username']),
            'export LENSE_API_GROUP="{0}"'.format(admin_user['group']),
            'export LENSE_API_KEY="{0}"'.format(admin_user['key'])  
        ], 'COMPLETE')
        
    def run(self):
        """
        Public method for bootstrapping Lense Engine.
        """
            
        # Get user input
        self.read_input(self.answers.get('engine', {}))
        
        # Create required directories and update the configuration
        self.mkdirs([self.ATTRS.LOG, self.ATTRS.RUN])
        self.update_config('engine')
            
        # Deploy the Apache configuration
        self.deploy_apache('engine')
        
        # Set log file permissions
        self.chown_logs('portal')
        
        # Bootstrap the database
        self.database()
        
        # Show to bootstrap complete summary
        self._bootstrap_complete()