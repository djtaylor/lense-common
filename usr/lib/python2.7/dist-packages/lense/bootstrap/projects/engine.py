from os import path, makedirs
from MySQLdb import connect as mysql_connect

# Lense Libraries
from lense.common.utils import rstring
from lense.common.http import HTTP_POST
from lense.common.vars import USERS, GROUPS
from lense.bootstrap.params import EngineParams
from lense.common.config import LenseConfigEditor
from lense.bootstrap.common import BootstrapCommon

class BootstrapEngine(BootstrapCommon):
    """
    Class object for handling bootstrap of the Lense API engine.
    """
    def __init__(self):
        super(BootstrapEngine, self).__init__('engine')
        
        # Bootstrap parameters
        self.params   = EngineParams()
        self.set_handlers(self.params.handlers)
        
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
            BOOTSTRAP.die(BOOTSTRAP.LOG.exception('Unable to connect to MySQL with root user: {0}'.format(str(e))))
    
    def _keyczart_create(self, enc_attrs):
        """
        Create a new database encryption key.
        """
        code, err = BOOTSTRAP.shell_exec(['keyczart', 'create', '--location={0}'.format(enc_attrs['dir']), '--purpose=crypt'])
        
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
        code, err = BOOTSTRAP.shell_exec(['keyczart', 'addkey', '--location={0}'.format(enc_attrs['dir']), '--status=primary', '--size=256'])
        
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
    
    def _create_groups(self):
        """
        Create the default administrator group.
        """
        for _group in self.params.groups:
            data = {
                'uuid': _group['uuid'],
                'name': _group['name'],
                'desc': _group['desc'],
                'protected': _group['protected']
            }
    
            # Launch the request handler
            self.launch_handler(path='group', data=data, method=HTTP_POST)
            BOOTSTRAP.FEEDBACK.success('Created Lense group: {0}'.format(data['name']))
    
    def _create_users(self):
        """
        Create the default administrator user account.
        """
        _users = []
        for user in self.params.users:
            _keys = user.get('_keys')
            
            # User password
            password = self.params.input.response.get(_keys['password'], rstring(12))
            
            # User data
            data = {
                'uuid': user['uuid'],
                'username': user['username'],
                'email': self.params.input.response.get(_keys['email'], user['email']),
                'password': password,
                'password_confirm': password    
            }
            
            # Create a new user object
            user_rsp = self.launch_handler(path='user', data=data, method=HTTP_POST)
            BOOTSTRAP.FEEDBACK.success('Created Lense account: {0}'.format(data['username']))
    
            # Add the user to the group
            self.launch_handler(path='group/member', data={
                'group': user['group'],
                'user': user_rsp['uuid']
            }, method=HTTP_POST)
            BOOTSTRAP.FEEDBACK.success('Account {0} setup as member of {1}'.format(data['username'], user['group']))
    
            # Append to the users object
            _users.append(user_rsp)
            
        # Return the users object
        return _users
    
    def _create_handlers(self):
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
                'rmap': _handler['rmap']
            }
            
            # Create the request handler
            handler = self.launch_handler(path='handler', data=data, method=HTTP_POST)
            BOOTSTRAP.FEEDBACK.success('Created database entry for handler "{0}": Path={1}, Method={2}'.format(_handler['name'], _handler['path'], _handler['method']))
    
            # Store the handler UUID
            _handler['uuid'] = handler['uuid']
    
    def _create_acl_keys(self):
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
            acl_key = self.launch_handler(path='acl/keys', data=data, method=HTTP_POST)
            BOOTSTRAP.FEEDBACK.success('Created database entry for ACL key "{0}"'.format(_acl_key['name']))
            
            # Store the new ACL key UUID
            _acl_key['uuid'] = acl_key['uuid']
            
        # Setup ACL objects
        self.params.acl.set_objects()
    
    def _create_acl_objects(self):
        """
        Create ACL object definitions.
        """
        for acl_object in self.params.acl.objects:
            self.launch_handler(path='acl/objects', data=acl_object, method=HTTP_POST)
            BOOTSTRAP.FEEDBACK.success('Created database entry for ACL object "{0}->{1}"'.format(acl_object['object_type'], acl_object['name']))
    
    def _create_handlers_access(self):
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
            if not k['type_global']: continue
            for u in k['handler_classes']:
                try:
                    BOOTSTRAP.OBJECTS.ACL.ACCESS('global').create(
                        acl = BOOTSTRAP.OBJECTS.ACL.KEYS.get(uuid=k['uuid']),
                        handler = BOOTSTRAP.OBJECTS.HANDLER.get(cls=u)
                    )
                    BOOTSTRAP.FEEDBACK.success('Granted global access to handler "{0}" with ACL "{1}"'.format(u, k['name']))
                except Exception as e:
                    BOOTSTRAP.die(BOOTSTRAP.LOG.exception('Failed to grant global access to handler "{0}" with ACL "{1}": {2}'.format(u, k['name'], str(e))))
    
    def _create_acl_access(self):
        """
        Setup ACL group access definitions.
        """
        for a in self.params.acl.set_access(self.params.acl.keys):
            try:
                BOOTSTRAP.OBJECTS.ACL.PERMISSIONS('global').create(
                    acl = BOOTSTRAP.OBJECTS.ACL.KEYS.get(uuid=a['acl']),
                    owner = BOOTSTRAP.OBJECTS.GROUP.get(uuid=a['owner']),
                    allowed = a['allowed']                                               
                )
                BOOTSTRAP.FEEDBACK.success('Granted global administrator access for ACL "{0}"'.format(a['acl_name']))
            except Exception as e:
                BOOTSTRAP.die(BOOTSTRAP.LOG.exception('Failed to grant global access for ACL "{0}": {1}'.format(a['acl_name'], str(e))))
    
    def _database_seed(self):
        """
        Seed the database with the base information needed to run Lense.
        """
        
        # Create the administrator group and user
        group = self._create_groups()
        users = self._create_users()
    
        # Store the new username and API key
        for user in users:
            if not user['username'] == USERS.ADMIN.NAME:
                continue
            
            # Get the user parameters
            user_params = self.params.get_user(USERS.ADMIN.NAME)
            
            # Default administrator
            self.params.set_user(USERS.ADMIN.NAME, 'key', user['api_key'])
            self.params.set_user(USERS.ADMIN.NAME, 'username', user['username'])
    
            # Update administrator info in the server configuration
            lce = LenseConfigEditor('ENGINE')
            lce.set('admin/user', user['username'])
            lce.set('admin/group', user_params['group'])
            lce.set('admin/key', user['api_key'])
            lce.save()
            BOOTSTRAP.FEEDBACK.success('[{0}] Set API administrator values'.format(self.ATTRS.CONF))
    
        # Create API handlers / ACL objects / ACL keys / access entries
        self._create_handlers()
        self._create_acl_keys()
        self._create_handlers_access()
        self._create_acl_objects()
        self._create_acl_access()
     
    def _database_user_exists(self):
        """
        Helper method for checking if the lense database user exists.
        """
        c = self._connection.cursor()
        retval = False if int(c.execute(self.params.db['query']['check_user'])) == 0 else True
        c.close()
        return retval
     
    def _database_exists(self):
        """
        Helper method for checking if the lense database exists.
        """
        c = self._connection.cursor()
        retval = False if int(c.execute(self.params.db['query']['check_db'])) == 0 else True
        c.close()
        return retval
     
    def _database(self):
        """
        Bootstrap the database and create all required tables and entries.
        """
            
        # Set database attributes
        self.params.set_db()
            
        # Test the database connection
        self._try_mysql_root()
            
        # Check if flushing existing data
        flushdb = BOOTSTRAP.ARGS.get('flushdb')
            
        # Create the database and user account
        try:
            c = self._connection.cursor()
            
            # If the database already exists
            if self._database_exists():
                BOOTSTRAP.ensure(flushdb, value=True, error='Database "{0}" already exists'.format(self.params.db['attrs']['name']))
            
                # Flush database
                c.execute(self.params.db['query']['delete_db'])
                BOOTSTRAP.FEEDBACK.info('Removing previous database...')
            
            # If the database user already exists
            if self._database_user_exists():
                BOOTSTRAP.ensure(flushdb, value=True, error='Database user "{0}" already exists'.format(self.params.db['attrs']['user']))
            
                # Flush database user
                c.execute(self.params.db['query']['delete_user'])
                BOOTSTRAP.FEEDBACK.info('Removing previous database user...')
            
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
            BOOTSTRAP.die(BOOTSTRAP.LOG.exception('Failed to bootstrap Lense database: {0}'.format(str(e))))
            
        # Close the connection
        c.close()
        
        # Set up database encryption
        self._database_encryption()
        
        # Run Django syncdb
        try:
            code, err = BOOTSTRAP.shell_exec(['python', '/usr/lib/python2.7/dist-packages/lense/engine/api/manage.py', 'migrate'])
            
            # Make sure the command ran successfully
            if not code == 0:
                BOOTSTRAP.die('Failed to sync Django application database: \n{0}'.format('\n'.join(err[1].split('\n'))))
                
            # Sync success
            BOOTSTRAP.FEEDBACK.success('Synced Django application database')
        except Exception as e:
            BOOTSTRAP.die(BOOTSTRAP.LOG.exception('Failed to sync Django application database: {0}'.format(str(e))))
            
        # Set up the database seed data
        self._database_seed()
        
    def _write_env(self, user, group, key):
        """
        Write the connection attributes to the current user's ~/.lense/env.sh file.
        """
        lense_home = path.expanduser('~/.lense')
        lense_env  = '{0}/env.sh'.format(lense_home)
        
        # Make sure the Lense home directory exists
        if not path.isdir(lense_home):
            makedirs(lense_home)
            
        # Write the environment shell file
        with open(lense_env, 'w') as f:
            f.write('export LENSE_API_USER="{0}"\n'.format(user))
            f.write('export LENSE_API_GROUP="{0}"\n'.format(group))
            f.write('export LENSE_API_KEY="{0}"\n'.format(key))
        BOOTSTRAP.FEEDBACK.success('Wrote Lense environment file: {0}'.format(lense_env))
        
    def _bootstrap_complete(self):
        """
        Brief summary of the completed bootstrap process.
        """
        
        # Get the admin user
        admin_user = self.params.get_user(USERS.ADMIN.NAME)
        
        # Write the Lense environment file
        self._write_env(admin_user['username'], admin_user['group'], admin_user['key'])
        
        # Store the administrator API key
        BOOTSTRAP.store('admin_key', admin_user['key'])
        
        # Print the summary
        BOOTSTRAP.FEEDBACK.block([
            'Finished bootstrapping Lense API engine!\n',
            'Please restart Apache to load the new virtual host(s). You can load the',
            'Lense environment file by adding the following to your ~/.bashrc file:\n',
            '[[ -f ~/.lense/env.sh ]] && . ~/.lense/env.sh' 
        ], 'COMPLETE')
        
    def run(self):
        """
        Public method for bootstrapping Lense Engine.
        """
            
        # Get user input
        self.read_input(BOOTSTRAP.ANSWERS.get('engine', {}))
        
        # Update the configuration
        self.update_config()
            
        # Deploy the Apache configuration
        self.deploy_apache()
        
        # Set log file permissions
        self.set_permissions(self.CONFIG.engine.log, owner='www-data:www-data')
        
        # Add the Apache user to the lense group
        self.group_add_user('www-data')
        
        # Bootstrap the database
        self._database()
        
        # Show to bootstrap complete summary
        self._bootstrap_complete()