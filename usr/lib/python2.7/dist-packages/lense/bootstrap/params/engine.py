from os import listdir
from json import loads as json_loads

# Lense Libraries
from lense.common.utils import rstring
from lense.common.vars import GROUPS, USERS, DB_ENCRYPT_DIR
from lense.bootstrap.common import BOOTSTRAP_DATA, BootstrapInput

class _EngineACL(object):
    """
    Handle bootstrapping ACL definitions.
    """
    def __init__(self):
        self.keys    = json_loads(open('{0}/acl/keys.json'.format(BOOTSTRAP_DATA), 'r').read())
        self.objects = None
        self.access  = None
        
    def _get_acl_key(self, name):
        """
        Return the UUID for an ACL key by name.
        """
        for k in self.keys:
            if k['name'] == name:
                return k['uuid']
        
    def set_objects(self):
        """
        Set attributes for ACL objects.
        """
        acl_objects = json_loads(open('{0}/acl/objects.json'.format(BOOTSTRAP_DATA), 'r').read())
        
        # Map default ACLs to UUIDs
        for obj in acl_objects:
            obj['def_acl'] = self._get_acl_key(obj['def_acl'])
        
        # Return mapped ACL objects
        return acl_objects
    
    def set_access(self, acls):
        """
        Set ACL access keys for the administrator group.
        
        @param acls: List of ACLs to grant the administrator group
        @type  acls: list
        """
        self.access = [{
            'acl':      acl['uuid'],
            'acl_name': acl['name'],
            'owner':    GROUPS.ADMIN.UUID,
            'allowed':  True
        } for acl in acls]
        
        # Return a copy of the access object
        return self.access

class _EngineInput(BootstrapInput):
    """
    Handle user input prompts and responses
    """
    def __init__(self):
        self.prompt   = self.load_prompts('engine')
        self.response = {}

    def set_response(self, key, value=None):
        """
        Set a response definition.
        """
        self.response[key] = value

class EngineParams(object):
    """
    Bootstrap parameters class object used to store and set the attributes
    required when using the bootstrap manager for the Lense API engine.
    """
    def __init__(self):
        
        # User input / ACL objects
        self.input    = _EngineInput()
        self.acl      = _EngineACL()
        
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
                "check_user": "SELECT User FROM mysql.user WHERE User='{0}'".format(attrs['user']),
                "create_user": "CREATE USER '{0}'@'{1}' IDENTIFIED BY '{2}'".format(attrs['user'], attrs['host'], attrs['passwd']),
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
                "name": GROUPS.SERVICE.NAME,
                "uuid": GROUPS.SERVICE.UUID,
                "desc": "Service accounts group",
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
                "email": None,
                "password": None,
                "key": None,
                "_keys": {
                    "email": "api_admin_email",
                    "password": "api_admin_password"
                }
            },
            {
                "username": USERS.SERVICE.NAME,
                "group": GROUPS.SERVICE.UUID,
                "email": None,
                "password": None,
                "key": None,
                "_keys": {
                    "email": "api_service_email",
                    "password": "api_service_password"
                }
            }
        ]
        
    def _set_handlers(self):
        """
        Load handler seed data.
        """
        handler_manifests = '{0}/handlers'.format(BOOTSTRAP_DATA)
        handlers = []
        
        # Start to load the handlers
        for h in listdir(handler_manifests):
            handler = '{0}/{1}'.format(handler_manifests, h)
            handlers.append(json_loads(open(handler, 'r').read()))
        return handlers