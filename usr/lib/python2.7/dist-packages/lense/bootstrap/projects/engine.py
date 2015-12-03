from os import environ, path
from subprocess import Popen
from json import dumps as json_dumps
from django import setup as django_setup
from MySQLdb import connect as mysql_connect
from lense.common.request import LenseWSGIRequest

# Set the Django settings module
environ['DJANGO_SETTINGS_MODULE'] = 'lense.engine.api.core.settings'

# Lense Libraries
from lense.common.utils import rstring
from lense.common.vars import USERS, GROUPS
from lense.bootstrap.params import EngineParams
from lense.common.config import LenseConfigEditor
from lense.bootstrap.common import BootstrapCommon

class BootstrapEngine(BootstrapCommon):
    """
    Class object for handling bootstrap of the Lense API engine.
    """
    def __init__(self, args, answers):
        super(BootstrapEngine, self).__init__('engine')
        
        # Arguments / answers
        self.args     = args
        self.answers  = answers
        
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
            BOOTSTRAP.FEEDBACK.success('Connected to MySQL using root user')
        except Exception as e:
            self.die('Unable to connect to MySQL with root user: {0}'.format(str(e)))
    
    def _keyczart_create(self, enc_attrs):
        """
        Create a new database encryption key.
        """
        code, err = self._shell_exec(['keyczart', 'create', '--location={0}'.format(enc_attrs['dir']), '--purpose=crypt'])
        
        # Failed to generate key
        if not code == 0:
            BOOTSTRAP.FEEDBACK.error('Failed to create database encryption key: {0}'.format(str(err)))
            return False
        
        # Generated encryption key
        BOOTSTRAP.FEEDBACK.success('Created database encryption key')
        return True
    
    def _keyczart_add(self, enc_attrs):
        """
        Add a new database encryption key.
        """
        code, err = self._shell_exec(['keyczart', 'addkey', '--location={0}'.format(enc_attrs['dir']), '--status=primary', '--size=256'])
        
        # Failed to add key
        if not code == 0:
            BOOTSTRAP.FEEDBACK.error('Failed to add database encryption key: {0}'.format(str(err)))
            return False
        
        # Added key
        BOOTSTRAP.FEEDBACK.success('Added database encryption key')
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
        if path.isfile(enc_attrs['key']) or path.isfile(enc_attrs['meta']):
            return BOOTSTRAP.FEEDBACK.warn('Database encryption key/meta properties already exist')
        
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
        for _group in self.params.groups:
            data = {
                'uuid': _group['uuid'],
                'name': _group['name'],
                'desc': _group['desc'],
                'protected': _group['protected']
            }
    
            group = obj(BOOTSTRAP.API.BARE(data=data, path='group')).launch()
            BOOTSTRAP.LOG.info('Received response from <{0}>: {1}'.format(str(obj), json_dumps(group)))
        
            # If the group was not created
            if not group['valid']:
                self.die('HTTP {0}: {1}'.format(group['code'], group['content']))
            BOOTSTRAP.FEEDBACK.success('Created Lense group: {0}'.format(group['data']['name']))
        
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
            data = {
                'username': user['username'],
                'group': user['group'],
                'email': self.params.input.response.get(_keys['email'], user['email']),
                'password': password,
                'password_confirm': password    
            }
            
            # Create a new user object
            user = obj(BOOTSTRAP.API.BARE(data=data, path='user')).launch()
            BOOTSTRAP.LOG.info('Received response from <{0}>: {1}'.format(str(obj), json_dumps(user)))
            
            # If the user was not created
            if not user['valid']:
                self.die('HTTP {0}: {1}'.format(user['code'], user['content']))
            BOOTSTRAP.FEEDBACK.success('Created Lense account: {0}'.format(data['username']))
        
            # Add to the users object
            _users.append(user)
        
        # Return the user object
        return _users
    
    def _create_handlers(self, obj):
        """
        Create API handler entries.
        """
        for _handler in self.params.handlers:
            data = {
                'path': _handler['path'],
                'name': _handler['name'],
                'desc': _handler['desc'],
                'method': _handler['method'],
                'mod': _handler['mod'],
                'cls': _handler['cls'],
                'protected': _handler['protected'],
                'enabled': _handler['enabled'],
                'object': _handler['object'],
                'object_key': _handler['object_key'],
                'allow_anon': _handler.get('allow_anon', False),
                'rmap': json_dumps(_handler['rmap'])
            }
            
            # Create the request handler
            handler = obj(BOOTSTRAP.API.BARE(data=data, path='handler')).launch()
            BOOTSTRAP.LOG.info('Received response from <{0}>: {1}'.format(str(obj), json_dumps(handler)))
            
            # If the handler was not created
            if not handler['valid']:
                self.die('HTTP {0}: {1}'.format(handler['code'], handler['content']))
            
            # Store the handler UUID
            _handler['uuid'] = handler['data']['uuid']
            BOOTSTRAP.FEEDBACK.success('Created database entry for handler "{0}": Path={1}, Method={2}'.format(_handler['name'], _handler['path'], _handler['method']))
    
    def _create_acl_keys(self, obj):
        """
        Create ACL key definitions.
        """
        for _acl_key in self.params.acl.keys:
            data = {
                "name": _acl_key['name'],
                "desc": _acl_key['desc'],
                "type_object": _acl_key['type_object'],
                "type_global": _acl_key['type_global']
            }
            
            # Create the ACL key
            acl_key = obj(BOOTSTRAP.API.BARE(data=data, path='acl')).launch()
            BOOTSTRAP.LOG.info('Received response from <{0}>: {1}'.format(str(obj), json_dumps(acl_key)))
            
            # If the ACL key was not created
            if not acl_key['valid']:
                self.die('HTTP {0}: {1}'.format(acl_key['code'], acl_key['content']))
                
            # Store the new ACL key UUID
            _acl_key['uuid'] = acl_key['data']['uuid']
            BOOTSTRAP.FEEDBACK.success('Created database entry for ACL key "{0}"'.format(_acl_key['name']))
            
        # Setup ACL objects
        self.params.acl.set_objects()
    
    def _create_acl_objects(self, obj):
        """
        Create ACL object definitions.
        """
        for _acl_object in self.params.acl.objects:
            data = {
                "type": _acl_object['type'],
                "name": _acl_object['name'],
                "acl_mod": _acl_object['acl_mod'],
                "acl_cls": _acl_object['acl_cls'],
                "acl_key": _acl_object['acl_key'],
                "obj_mod": _acl_object['obj_mod'],
                "obj_cls": _acl_object['obj_cls'],
                "obj_key": _acl_object['obj_key'],
                "def_acl": _acl_object['def_acl']
            }
            
            # Create the ACL object
            acl_object = obj(BOOTSTRAP.API.BARE(data=data, path='acl/objects')).launch()
            BOOTSTRAP.LOG.info('Received response from <{0}>: {1}'.format(str(obj), json_dumps(acl_object)))
            
            # If the ACL object was not created
            if not acl_object['valid']:
                self.die('HTTP {}: {}'.format(acl_object['code'], acl_object['content']))
            BOOTSTRAP.FEEDBACK.success('Created database entry for ACL object "{0}->{1}"'.format(_acl_object['type'], _acl_object['name']))
    
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
                    BOOTSTRAP.FEEDBACK.success('Granted global access to handler "{0}" with ACL "{1}"'.format(u, k['name']))
    
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
                BOOTSTRAP.FEEDBACK.success('Granted global administrator access for ACL "{0}"'.format(a['acl_name']))
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
        django_setup()
        
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
            BOOTSTRAP.FEEDBACK.success('[{0}] Set API administrator values'.format(self.ATTRS.CONF))
    
        # Create API handlers / ACL objects / ACL keys / access entries
        self._create_handlers(Handler_Create)
        self._create_acl_keys(ACL_Create)
        self._create_handlers_access(ACLGlobalAccess, ACLKeys, Handlers)
        self._create_acl_objects(ACLObjects_Create)
        self._create_acl_access(ACLGroupPermissions_Global, ACLKeys, APIGroups)
     
    def _database_user_exists(self):
        """
        Helper method for checking if the lense database user exists.
        """
        c = self._connection.cursor()
        return False if int(c.execute(self.params.db['query']['check_user'])) == 0 else True
        c.close()
     
    def _database_exists(self):
        """
        Helper method for checking if the lense database exists.
        """
        c = self._connection.cursor()
        return False if int(c.execute(self.params.db['query']['check_db'])) == 0 else True
        c.close()
     
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
            
            # If the database already exists
            if self._database_exists():
                self.die('Database "{0}" already exists'.format(self.params.db['attrs']['name']))
            
            # If the database user already exists
            if self._database_user_exists():
                self.die('Database user "{0}" already exists'.format(self.params.db['attrs']['user']))
            
            # Create the database    
            c.execute(self.params.db['query']['create_db'])
            BOOTSTRAP.FEEDBACK.success('Created database "{0}"'.format(self.params.db['attrs']['name']))
            
            # Create the database user
            c.execute(self.params.db['query']['create_user'])
            BOOTSTRAP.FEEDBACK.success('Created database user "{0}"'.format(self.params.db['attrs']['user']))
                
            # Grant privileges
            c.execute(self.params.db['query']['grant_user'])
            c.execute(self.params.db['query']['flush_priv'])
            BOOTSTRAP.FEEDBACK.success('Granted database permissions to user "{0}"'.format(self.params.db['attrs']['user']))
            
        except Exception as e:
            self.die('Failed to bootstrap Lense database: {0}'.format(str(e)))
            
        # Close the connection
        c.close()
        
        # Set up database encryption
        self._database_encryption()
        
        # Run Django syncdb
        try:
            code, err = self._shell_exec(['python', '/usr/lib/python2.7/dist-packages/lense/engine/api/manage.py', 'migrate'])
            
            # Make sure the command ran successfully
            if not code == 0:
                self.die('Failed to sync Django application database: {0}'.format(str(err)))
                
            # Sync success
            BOOTSTRAP.FEEDBACK.success('Synced Django application database')
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
        BOOTSTRAP.FEEDBACK.block([
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
        
        # Update the configuration
        self.update_config()
            
        # Deploy the Apache configuration
        self.deploy_apache()
        
        # Set log file permissions
        self.set_permissions(self.ATTRS.LOG, owner='www-data:www-data')
        
        # Add the Apache user to the lense group
        self.group_add_user('www-data')
        
        # Bootstrap the database
        self._database()
        
        # Show to bootstrap complete summary
        self._bootstrap_complete()