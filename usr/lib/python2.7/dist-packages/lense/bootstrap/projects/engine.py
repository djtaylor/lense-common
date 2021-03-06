from os import path, makedirs
from MySQLdb import connect as mysql_connect

# Lense Libraries
from lense.common.utils import rstring
from lense.common.http import HTTP_POST, HTTP_GET
from lense.common.vars import USERS, GROUPS
from lense.bootstrap.params import EngineParams
from lense.common.config import LenseConfigEditor
from lense.bootstrap.common import BootstrapCommon
from lense.common.request import LenseWSGIRequest

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
        
        # Setup the request data
        LENSE.REQUEST.set(LenseWSGIRequest.get(path='bootstrap', data={}, method=HTTP_GET))
        
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
        for group in self.params.groups:
            group_object = LENSE.OBJECTS.GROUP.create(**{
                'uuid': group['uuid'],
                'name': group['name'],
                'desc': group['desc'],
                'protected': group['protected']                                          
            })
            BOOTSTRAP.FEEDBACK.success('Created Lense group: {0}'.format(group_object.name))
    
    def _create_users(self):
        """
        Create the default administrator user account.
        """
        users = []
        for user in self.params.users:
            keys = user.get('_keys')
            
            # User password / email
            password = self.params.input.response.get(keys['password'], rstring(12))
            email    = self.params.input.response.get(keys['email'], user['email'])
            
            # Create a new user object
            user_object = LENSE.OBJECTS.USER.create(**{
                'uuid': user['uuid'],
                'username': user['username'],
                'email': email,
                'password': password,
                'group': user['group']
            })
            BOOTSTRAP.FEEDBACK.success('Created Lense account: {0}'.format(user_object.username))
    
            # Append to the users object
            users.append(LENSE.OBJECTS.dump(user_object))
            
        # Return the users object
        return users
    
    def _create_handlers(self):
        """
        Create API handler entries.
        """
        for handler in self.params.handlers:
            handler_object = LENSE.OBJECTS.HANDLER.create(**{
                'path': handler['path'],
                'name': handler['name'],
                'desc': handler['desc'],
                'method': handler['method'],
                'protected': handler['protected'],
                'enabled': handler['enabled'],
                'allow_anon': handler.get('allow_anon', False),
                'manifest': handler['manifest']                                      
            })
            BOOTSTRAP.FEEDBACK.success('Created database entry for handler "{0}": Path={1}, Method={2}'.format(handler['name'], handler['path'], handler['method']))
    
            # Store the handler UUID
            handler['uuid'] = handler_object.uuid
         
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
    
        # Create API handlers
        self._create_handlers()
     
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