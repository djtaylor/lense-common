from os import listdir, path
from json import loads as json_loads

# Lense Libraries
from lense.common.utils import rstring
from lense.bootstrap.common import BootstrapInput
from lense.common.vars import GROUPS, USERS, DB_ENCRYPT_DIR, SHARE

class EngineParams(object):
    """
    Bootstrap parameters class object used to store and set the attributes
    required when using the bootstrap manager for the Lense API engine.
    """
    def __init__(self):
        
        # User input / ACL objects
        self.input    = BootstrapInput('engine')
        
        # Groups/users/database/file parameters
        self.groups   = self._set_groups()
        self.users    = self._set_users()
        self.handlers = self._set_handlers()
        self.db       = None
    
    def get_config(self):
        """
        Load the updated server configuration
        """
        
        # Generate a new Django secret
        django_secret = "'{0}'".format(rstring(64))
        
        # Return the updated server configuration
        return {
            'engine': {
                'host': self.input.response.get('api_host'),
                'port': self.input.response.get('api_port'),
                'secret': django_secret      
            },
            'db': {
                'host': self.input.response.get('db_host'),
                'port': self.input.response.get('db_port'),
                'user': self.input.response.get('db_user'),
                'password': self.input.response.get('db_user_password'),
                'name': self.input.response.get('db_name')
            },
            'portal': {
                'host': self.input.response.get('portal_host'),
                'port': self.input.response.get('portal_port')
            },
            'socket': {
                'host': self.input.response.get('socket_host'),
                'port': self.input.response.get('socket_port')
            }    
        }
    
    def set_db(self):
        """
        Set default database queries.
        """
        
        # Database attributes
        attrs = {
            'name': self.input.response.get('db_name'),
            'user': self.input.response.get('db_user'),
            'host': self.input.response.get('db_host'),
            'passwd': self.input.response.get('db_user_password'),
            'encryption': {
                'dir':  DB_ENCRYPT_DIR,
                'key':  '{0}/1'.format(DB_ENCRYPT_DIR),
                'meta': '{0}/meta'.format(DB_ENCRYPT_DIR)
            }
        }
        
        # Return the database queries
        self.db = {
            "attrs": attrs,
            "query": {
                "check_db": "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='{0}'".format(attrs['name']),
                "create_db": "CREATE DATABASE IF NOT EXISTS {0}".format(attrs['name']),
                "delete_db": "DROP SCHEMA {0}".format(attrs['name']),
                "check_user": "SELECT User FROM mysql.user WHERE User='{0}'".format(attrs['user']),
                "create_user": "CREATE USER '{0}'@'{1}' IDENTIFIED BY '{2}'".format(attrs['user'], attrs['host'], attrs['passwd']),
                "delete_user": "DROP USER '{0}'@'{1}'".format(attrs['user'], attrs['host']),
                "grant_user": "GRANT ALL PRIVILEGES ON {0}.* TO '{1}'@'{2}'".format(attrs['name'], attrs['user'], attrs['host']),
                "flush_priv": "FLUSH PRIVILEGES"
            }
        }
        
    def _set_groups(self):
        """
        Set default group parameters.
        """
        return [
            {
                "name": GROUPS.ADMIN.NAME,
                "uuid": GROUPS.ADMIN.UUID,
                "desc": "Default administrator group",
                "protected": True
            },
            {
                "name": GROUPS.USER.NAME,
                "uuid": GROUPS.USER.UUID,
                "desc": "Default user group",
                "protected": True
            }
        ]
        
    def get_user(self, name):
        """
        Extract attributes for a specific user.
        """
        for user in self.users:
            if user['username'] == name:
                return user
        return None
        
    def set_user(self, name, key, value):
        """
        Set user attributes.
        """
        for user in self.users:
            if user['username'] == name:
                user[key] = value
        
    def _set_users(self):
        """
        Set default user parameters.
        """
        return [
            {
                "username": USERS.ADMIN.NAME,
                "group": GROUPS.ADMIN.UUID,
                "uuid": USERS.ADMIN.UUID,
                "email": None,
                "password": None,
                "key": None,
                "_keys": {
                    "email": "api_admin_email",
                    "password": "api_admin_password"
                }
            },
            {
                "username": USERS.USER.NAME,
                "group": GROUPS.USER.UUID,
                "uuid": USERS.USER.UUID,
                "email": None,
                "password": None,
                "key": None,
                "_keys": {
                    "email": "api_user_email",
                    "password": "api_user_password"
                }
            }
        ]
        
    def _set_handlers(self):
        """
        Load handler seed data.
        """
        handler_core = '{0}/handlers'.format(SHARE.BOOTSTRAP)
        handler_manifest = '{0}/manifests'.format(SHARE.BOOTSTRAP)
        
        # Store handlers
        handlers = []
        
        # Start to load the handlers
        for h in listdir(handler_core):
            handler  = json_loads(open('{0}/{1}'.format(handler_core, h), 'r').read())
            manifest = '{0}/{1}'.format(handler_manifest, h) 
            
            # If using new style manifests
            if path.isfile(manifest):
                handler['use_manifest'] = True
                handler['manifest']     = json_loads(open(manifest, 'r').read())
                            
            # Store the handler
            handlers.append(handler)
        return handlers