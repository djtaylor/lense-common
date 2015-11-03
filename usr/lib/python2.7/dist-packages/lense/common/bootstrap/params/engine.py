from collections import OrderedDict

# Lense Libraries
from lense.common.utils import rstring
from lense.common.vars import G_ADMIN, U_ADMIN, DB_ENCRYPT_DIR
from lense.common.http import HTTP_GET, HTTP_POST, HTTP_PUT, HTTP_DELETE

class _EngineACL(object):
    """
    Handle bootstrapping ACL definitions.
    """
    def __init__(self):
        self.keys    = self._set_keys()
        self.objects = None
        self.access  = None
        
    def set_access(self, acls):
        """
        Set ACL access keys for the administrator group.
        
        @param acls: List of ACLs to grant the administrator group
        @type  acls: list
        """
        _access = []
        for acl in acls:
            _access.append({
                "acl": acl['uuid'],
                "acl_name": acl['name'],
                "owner": G_ADMIN,
                "allowed": True          
            })
        self.access = _access
        return _access
        
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
        self.objects = [
            {
                "type": "utility",
                "name": "API Utility",
                "acl_mod": "lense.engine.api.app.gateway.models",
                "acl_cls": "DBGatewayACLGroupObjectUtilityPermissions",
                "acl_key": "utility",
                "obj_mod": "lense.engine.api.app.gateway.models",
                "obj_cls": "DBGatewayUtilities",
                "obj_key": "uuid",
                "def_acl": self._get_acl_key('util.view')
            },
            {
                "type": "group",
                "name": "API Group",
                "acl_mod": "lense.engine.api.app.gateway.models",
                "acl_cls": "DBGatewayACLGroupObjectGroupPermissions",
                "acl_key": "group",
                "obj_mod": "lense.engine.api.app.group.models",
                "obj_cls": "DBGroupDetails",
                "obj_key": "uuid",
                "def_acl": self._get_acl_key('group.view')
            },
            {
                "type": "user",
                "name": "API User",
                "acl_mod": "lense.engine.api.app.gateway.models",
                "acl_cls": "DBGatewayACLGroupObjectUserPermissions",
                "acl_key": "user",
                "obj_mod": "lense.engine.api.app.user.models",
                "obj_cls": "DBUser",
                "obj_key": "uuid",
                "def_acl": self._get_acl_key('user.view')
            },
            {
                "type": "connector",
                "name": "API Connector",
                "acl_mod": "lense.engine.api.app.gateway.models",
                "acl_cls": "DBGatewayACLGroupObjectConnectorPermissions",
                "acl_key": "connector",
                "obj_mod": "lense.engine.api.app.connector.models",
                "obj_cls": "DBConnectors",
                "obj_key": "uuid",
                "def_acl": self._get_acl_key('connector.view')
            },
            {
                "type": "integrator",
                "name": "API Integrator",
                "acl_mod": "lense.engine.api.app.gateway.models",
                "acl_cls": "DBGatewayACLGroupObjectIntegratorPermissions",
                "acl_key": "integrator",
                "obj_mod": "lense.engine.api.app.integrator.models",
                "obj_cls": "DBIntegrators",
                "obj_key": "uuid",
                "def_acl": self._get_acl_key('integrator.view')
            }
        ]
    
    def _set_keys(self):
        """
        Set attributes for ACL keys.
        """
        return [
            {
                "name": "token.get",
                "desc": "ACL for allowing API token requests.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "GatewayTokenGet"
                ]
            },
            {
                "name": "connector.view",
                "desc": "ACL for allowing read-only access to API connectors.",
                "type_object": True,
                "type_global": False,
                "util_classes": [
                    "ConnectorsGet"
                ]
            },
            {
                "name": "connector.admin",
                "desc": "ACL for allowing administration of API connectors.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "ConnectorsGet",
                    "ConnectorsCreate",
                    "ConnectorsUpdate",
                    "ConnectorsDelete"
                ]
            },
            {
                "name": "integrator.view",
                "desc": "ACL for allowing read-only access to API integrators.",
                "type_object": True,
                "type_global": False,
                "util_classes": [
                    "IntegratorsGet"
                ]
            },
            {
                "name": "integrator.admin",
                "desc": "ACL for allowing administration of API integrators.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "IntegratorsGet",
                    "IntegratorsCreate",
                    "IntegratorsUpdate",
                    "IntegratorsDelete"
                ]
            },
            {
                "name": "user.admin",
                "desc": "ACL for allowing global administration of users.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "UserGet",
                    "UserCreate",
                    "UserDelete",
                    "UserEnable",
                    "UserDisable",
                    "UserResetPassword"
                ]
            },
            {
                "name": "user.view",
                "desc": "ACL for allowing read-only access to user objects.",
                "type_object": True,
                "type_global": False,
                "util_classes": [
                    "UserGet"
                ]
            },
            {
                "name": "group.admin",
                "desc": "ACL for allowing global administration of groups.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "GroupGet",
                    "GroupCreate",
                    "GroupUpdate",
                    "GroupDelete",
                    "GroupMemberAdd",
                    "GroupMemberRemove"
                ]
            },
            {
                "name": "group.view",
                "desc": "ACL for allowing read-only access to group objects.",
                "type_object": True,
                "type_global": False,
                "util_classes": [
                    "GroupGet"
                ]
            },
            {
                "name": "util.admin",
                "desc": "ACL for allowing administration of API utilities.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "GatewayUtilitiesGet",
                    "GatewayUtilitiesCreate",
                    "GatewayUtilitiesSave",
                    "GatewayUtilitiesValidate",
                    "GatewayUtilitiesDelete",
                    "GatewayUtilitiesClose",
                    "GatewayUtilitiesOpen"
                ]
            },
            {
                "name": "util.view",
                "desc": "ACL for allowing read-only access to utility objects.",
                "type_object": True,
                "type_global": False,
                "util_classes": [
                    "GatewayUtilitiesGet"
                ]
            },
            {
                "name": "acl.view",
                "desc": "ACL for allowing read-only access to ACL definitions.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                     "GatewayACLGet"            
                ]
            },
            {
                "name": "acl.admin",
                "desc": "ACL for allowing administration of ACL definitions.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                     "GatewayACLGet",
                     "GatewayACLCreate",
                     "GatewayACLDelete",
                     "GatewayACLUpdate"       
                ]
            },
            {
                "name": "acl_object.view",
                "desc": "ACL for allowing read-only access to ACL object definitions.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "GatewayACLObjectsGet"
                ]
            },
            {
                "name": "acl_object.admin",
                "desc": "ACL for allowing administration of ACL object definitions.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "GatewayACLObjectsGet",
                    "GatewayACLObjectsCreate",
                    "GatewayACLObjectsDelete",
                    "GatewayACLObjectsUpdate"
                ]
            }
        ]

class _EngineInput(object):
    """
    Handle user input prompts and responses
    """
    def __init__(self):
        self.prompt   = self._set_prompts()
        self.response = {}

    def set_response(self, key, value=None):
        """
        Set a response definition.
        """
        self.response[key] = value

    def _set_prompts(self):
        """
        Set attributes for input prompts.
        """
        
        # Prompt collection
        _prompt = OrderedDict()
        
        # Database entries
        _prompt['database'] = {
            "label": "Database Configuration",
            "attrs": OrderedDict({
                "db_host": {
                    "type": "str",
                    "default": "localhost",
                    "prompt": "Please enter the hostname or IP address of the MySQL database server (localhost): ",
                    "value": None
                },
                "db_port": {
                    "type": "str",
                    "default": "3306",
                    "prompt": "Please enter the port to connect to the MySQL database server (3306): ",
                    "value": None
                },
                "db_name": {
                    "type": "str",
                    "default": "lense",
                    "prompt": "Please enter the name of the database to use/create for Lense (lense): ",
                    "value": None
                },
                "db_user": {
                    "type": "str",
                    "default": "lense",
                    "prompt": "Please enter the name of the primary non-root database user (lense): ",
                    "value": None
                },
                "db_name": {
                    "type": "str",
                    "default": "lense",
                    "prompt": "Please enter the name of the database to use (lense): ",
                    "value": None
                },
                "db_user_password": {
                    "type": "pass",
                    "default": None,
                    "prompt": "Please enter the password for the primary non-root database user: ",
                    "value": None
                },
                "db_root_password": {
                    "type": "pass",
                    "default": None,
                    "prompt": "Please enter the root password for the database server: ",
                    "value": None
                }             
            })             
        }
        
        # API engine entries
        _prompt['engine'] = {
            "label": "API Engine Configuration",
            "attrs": OrderedDict({
                "api_admin_password": {
                    "type": "pass",
                    "default": None,
                    "prompt": "Please enter a password for the default administrator account: ",
                    "value": None
                },
                "api_admin_email": {
                    "type": "str",
                    "default": None,
                    "prompt": "Please enter the email address for the default administrator account: ",
                    "value": None
                },
                "api_host": {
                    "type": "str",
                    "default": "localhost",
                    "prompt": "Please enter the hostname for the API server (localhost): ",
                    "value": None
                },
                "api_port": {
                    "type": "str",
                    "default": "10550",
                    "prompt": "Please enter the port for the API server (10550): ",
                    "value": None
                } 
            })             
        }
        
        # API portal entries
        _prompt['portal'] = {
            "label": "API Portal Configuration",
            "attrs": OrderedDict({
                "portal_host": {
                    "type": "str",
                    "default": "localhost",
                    "prompt": "Please enter the hostname for the portal server (localhost): ",
                    "value": None
                },
                "portal_port": {
                    "type": "str",
                    "default": "80",
                    "prompt": "Please enter the port for the portal server (80): ",
                    "value": None
                }
            })               
        }
        
        # API proxy socket server entries
        _prompt['socket'] = {
            "label": "API Socket.IO Proxy Configuration",
            "attrs": OrderedDict({
                "socket_host": {
                    "type": "str",
                    "default": "localhost",
                    "prompt": "Please enter the hostname for the socket server (localhost): ",
                    "value": None
                },
                "socket_port": {
                    "type": "str",
                    "default": "10551",
                    "prompt": "Please enter the port for the socket server (10551): ",
                    "value": None
                }
            })             
        }
        
        # Return the prompt object
        return _prompt

class EngineParams(object):
    """
    Bootstrap parameters class object used to store and set the attributes
    required when using the bootstrap manager for the Lense API engine.
    """
    def __init__(self):
        
        # User input / ACL objects
        self.input  = _EngineInput()
        self.acl    = _EngineACL()
        
        # Groups/users/database/file parameters
        self.group  = self._set_group()
        self.user   = self._set_user()
        self.utils  = self._set_utils()
        self.db     = None
    
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
        db_attrs = {
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
            "attrs": db_attrs,
            "query": {
                "create_db": "CREATE DATABASE IF NOT EXISTS {0}".format(db_attrs['name']),
                "create_user": "CREATE USER '{0}'@'{1}' IDENTIFIED BY '{2}'".format(db_attrs['user'], db_attrs['host'], db_attrs['passwd']),
                "grant_user": "GRANT ALL PRIVILEGES ON {0}.* TO '{1}'@'{2}'".format(db_attrs['name'], db_attrs['user'], db_attrs['host']),
                "flush_priv": "FLUSH PRIVILEGES"
            }
        }
        
    def _set_group(self):
        """
        Set default group parameters.
        """
        return {
            "name": U_ADMIN,
            "uuid": G_ADMIN,
            "desc": "Default administrator group",
            "protected": True   
        }
        
    def _set_user(self):
        """
        Set default user parameters.
        """
        return {
            "username": U_ADMIN,
            "group": G_ADMIN,
            "email": None,
            "password": None,
            "key": None
        }
        
    def _set_utils(self):
        """
        Set default utility parameters
        """
        
        # Set the utility modules
        umod = {
            'gateway': 'lense.engine.api.app.gateway.utils',
            'group': 'lense.engine.api.app.group.utils',
            'user': 'lense.engine.api.app.user.utils',
            'callback': 'lense.engine.api.app.callback.utils',
            'connector': 'lense.engine.api.app.connector.utils',
            'integrator': 'lense.engine.api.app.integrator.utils'
        }
        
        
        # Return the database parameters
        return [
            {
                "cls": "CallbackHandle",
                "name": "Callback_Handle",
                "path": "callback",
                "method": HTTP_GET,
                "desc": "Handle callbacks from 3rd party APIs",
                "mod": umod['callback'],
                "protected": True,
                "enabled": True,
                "object": None,
                "object_key": None,
                "allow_anon": True,
                "rmap": {
                    "_required": ["provider"],
                    "_optional": ["*"],
                    "_type": "dict",
                    "_children": {
                        "provider": {
                            "_type": "str"
                        }
                    }
                }
            },
            {
                "cls": "GatewayTokenGet",
                "name": "Token_Get",
                "path": "gateway/token",
                "method": HTTP_GET,
                "desc": "Make a token request to the API gateway",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": None,
                "object_key": None,
                "allow_anon": True,
                "rmap": {
                    "_required": [],
                    "_optional": [],
                    "_type": "dict"
                }
            },
            {
                "cls": "GatewayACLGet",
                "name": "ACL_Get",
                "path": "gateway/acl",
                "method": HTTP_GET,
                "desc": "Retrieve an ACL definition",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": None,
                "object_key": None,
                "rmap": {
                    "_required": [],
                    "_optional": ["acl"],
                    "_type": "dict",
                    "_children": {
                        "acl": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GatewayACLCreate",
                "name": "ACL_Create",
                "path": "gateway/acl",
                "method": HTTP_POST,
                "desc": "Create a new ACL definition",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": None,
                "object_key": None,
                "rmap": {
                    "_required": ["name", "desc", "object", "global"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "name": {
                            "_type": "str"
                        },
                        "desc": {
                            "_type": "str"
                        },
                        "object": {
                            "_type": "bool"
                        },
                        "global": {
                            "_type": "bool"
                        }
                    }
                }
            },
            {
                "cls": "GatewayACLDelete",
                "name": "ACL_Delete",
                "path": "gateway/acl",
                "method": HTTP_DELETE,
                "desc": "Delete an existing ACL definition",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": None,
                "object_key": None,
                "rmap": {
                    "_required": [],
                    "_optional": ["acl"],
                    "_type": "dict",
                    "_children": {
                        "acl": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GatewayACLUpdate",
                "name": "ACL_Update",
                "path": "gateway/acl",
                "method": HTTP_PUT,
                "desc": "Update an existing ACL definition",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": None,
                "object_key": None,
                "rmap": {
                    "_required": ["acl"],
                    "_optional": ["name", "desc", "object", "global"],
                    "_type": "dict",
                    "_children": {
                        "acl": {
                            "_type": "uuid"
                        },
                        "name": {
                            "_type": "str"
                        },
                        "desc": {
                            "_type": "str"
                        },
                        "object": {
                            "_type": "bool"
                        },
                        "global": {
                            "_type": "bool"
                        }
                    }
                }
            },
            {
                "cls": "GatewayACLObjectsGet",
                "name": "ACLObjects_Get",
                "path": "gateway/acl/objects",
                "method": HTTP_GET,
                "desc": "Get a listing of ACL objects",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": None,
                "object_key": None,
                "rmap": {
                    "_required": [],
                    "_optional": ["acl_object"],
                    "_type": "dict",
                    "_children": {
                        "acl_object": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GatewayACLObjectsUpdate",
                "name": "ACLObjects_Update",
                "path": "gateway/acl/objects",
                "method": HTTP_PUT,
                "desc": "Update an ACL object definition",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": None,
                "object_key": None,
                "rmap": {
                    "_required": ["acl_object"],
                    "_optional": ["type", "name", "acl_obj", "acl_cls", "acl_key", "obj_mod", "obj_cls", "obj_key", "def_acl"],
                    "_type": "dict",
                    "_children": {
                        "acl_object": {
                            "_type": "uuid"
                        },
                        "type": {
                            "_type": "str"
                        },
                        "name": {
                            "_type": "str"
                        },
                        "acl_obj": {
                            "_type": "str"
                        },
                        "acl_cls": {
                            "_type": "str"
                        },
                        "acl_key": {
                            "_type": "str"
                        },
                        "obj_mod": {
                            "_type": "str"
                        },
                        "obj_cls": {
                            "_type": "str"
                        },
                        "obj_key": {
                            "_type": "str"
                        },
                        "def_acl": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GatewayACLObjectsCreate",
                "name": "ACLObjects_Create",
                "path": "gateway/acl/objects",
                "method": HTTP_POST,
                "desc": "Create a new ACL object definition",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": None,
                "object_key": None,
                "rmap": {
                    "_required": ["type", "name", "acl_obj", "acl_cls", "acl_key", "obj_mod", "obj_cls", "obj_key", "def_acl"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "type": {
                            "_type": "str"
                        },
                        "name": {
                            "_type": "str"
                        },
                        "acl_obj": {
                            "_type": "str"
                        },
                        "acl_cls": {
                            "_type": "str"
                        },
                        "acl_key": {
                            "_type": "str"
                        },
                        "obj_mod": {
                            "_type": "str"
                        },
                        "obj_cls": {
                            "_type": "str"
                        },
                        "obj_key": {
                            "_type": "str"
                        },
                        "def_acl": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GatewayACLObjectsDelete",
                "name": "ACLObjects_Delete",
                "path": "gateway/acl/objects",
                "method": HTTP_DELETE,
                "desc": "Delete an existing ACL object definition",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": None,
                "object_key": None,
                "rmap": {
                    "_required": ["acl_object"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "acl_object": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GatewayUtilitiesGet",
                "name": "Utilities_Get",
                "path": "gateway/utilities",
                "method": HTTP_GET,
                "desc": "Get a listing of API utilities",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": "utility",
                "object_key": "uuid",
                "rmap": {
                    "_required": [],
                    "_optional": ["utility"],
                    "_type": "dict",
                    "_children": {
                        "utility": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GatewayUtilitiesOpen",
                "name": "Utilities_Open",
                "path": "gateway/utilities/open",
                "method": HTTP_PUT,
                "desc": "Open an API utility for editing",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": "utility",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["utility"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "utility": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GatewayUtilitiesClose",
                "name": "Utilities_Close",
                "path": "gateway/utilities/close",
                "method": HTTP_PUT,
                "desc": "Close the editing lock on an API utility",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": "utility",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["utility"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "utility": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GatewayUtilitiesValidate",
                "name": "Utilities_Validate",
                "path": "gateway/utilities/validate",
                "method": HTTP_PUT,
                "desc": "Validate changes to an API utility",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": "utility",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["utility"],
                    "_optional": ["path", "name", "desc", "method", "mod", "cls", "utils", "rmap", "object", "object_key", "protected", "enabled", "allow_anon"],
                    "_type": "dict",
                    "_children": {
                        "utility": {
                            "_type": "uuid"
                        },
                        "name": {
                            "_type": "str"
                        },
                        "path": {
                            "_type": "str"
                        },
                        "desc": {
                            "_type": "str"
                        },
                        "method": {
                            "_type": "str",
                            "_values": ["PUT", "POST", "GET", "DELETE"]
                        },
                        "mod": {
                            "_type": "str"
                        },
                        "cls": {
                            "_type": "str"
                        },
                        "utils": {
                            "_type": "list"
                        },
                        "rmap": {
                            "_type": "dict"
                        },
                        "object": {
                            "_type": "str"
                        },
                        "object_key": {
                            "_type": "str"
                        },
                        "protected": {
                            "_type": "bool"
                        },
                        "enabled": {
                            "_type": "bool"
                        },
                        "allow_anon": {
                            "_type": "bool"
                        }
                    }
                }
            },
            {
                "cls": "GatewayUtilitiesSave",
                "name": "Utilities_Save",
                "path": "gateway/utilities",
                "method": HTTP_PUT,
                "desc": "Save changes to an API utility",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": "utility",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["utility"],
                    "_optional": ["path", "name", "desc", "method", "mod", "cls", "utils", "rmap", "object", "object_key", "protected", "enabled", "allow_anon"],
                    "_type": "dict",
                    "_children": {
                        "utility": {
                            "_type": "uuid"
                        },
                        "name": {
                            "_type": "str"
                        },
                        "path": {
                            "_type": "str"
                        },
                        "desc": {
                            "_type": "str"
                        },
                        "method": {
                            "_type": "str",
                            "_values": ["PUT", "POST", "GET", "DELETE"]
                        },
                        "mod": {
                            "_type": "str"
                        },
                        "cls": {
                            "_type": "str"
                        },
                        "utils": {
                            "_type": "list"
                        },
                        "rmap": {
                            "_type": "dict"
                        },
                        "object": {
                            "_type": "str"
                        },
                        "object_key": {
                            "_type": "str"
                        },
                        "protected": {
                            "_type": "bool"
                        },
                        "enabled": {
                            "_type": "bool"
                        },
                        "allow_anon": {
                            "_type": "bool"
                        }
                    }
                }
            },
            {
                "cls": "GatewayUtilitiesCreate",
                "name": "Utilities_Create",
                "path": "gateway/utilities",
                "method": HTTP_POST,
                "desc": "Create a new API utility",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": "utility",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["path", "name", "desc", "method", "mod", "cls", "utils", "rmap", "object", "object_key", "protected", "enabled", "allow_anon"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "path": {
                            "_type": "str"
                        },
                        "name": {
                            "_type": "str"
                        },
                        "desc": {
                            "_type": "str"
                        },
                        "method": {
                            "_type": "str",
                            "_values": ["PUT", "POST", "GET", "DELETE"]
                        },
                        "mod": {
                            "_type": "str"
                        },
                        "cls": {
                            "_type": "str"
                        },
                        "utils": {
                            "_type": "list"
                        },
                        "rmap": {
                            "_type": "dict"
                        },
                        "object": {
                            "_type": "str"
                        },
                        "object_key": {
                            "_type": "str"
                        },
                        "protected": {
                            "_type": "bool"
                        },
                        "enabled": {
                            "_type": "bool"
                        },
                        "allow_anon": {
                            "_type": "bool"
                        }
                    }
                }
            },
            {
                "cls": "GatewayUtilitiesDelete",
                "name": "Utilities_Delete",
                "path": "gateway/utilities",
                "method": HTTP_DELETE,
                "desc": "Delete an existing API utility",
                "mod": umod['gateway'],
                "protected": True,
                "enabled": True,
                "object": "utility",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["utility"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "utility": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GroupMemberRemove",
                "name": "Group_RemoveMember",
                "path": "group/member",
                "method": HTTP_DELETE,
                "desc": "Remove a user from an API group",
                "mod": umod['group'],
                "protected": True,
                "enabled": True,
                "object": "group",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["group", "user"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "group": {
                            "_type": "uuid"
                        },
                        "user": { 
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GroupMemberAdd",
                "name": "Group_AddMember",
                "path": "group/member",
                "method": HTTP_POST,
                "desc": "Add a user to an API group",
                "mod": umod['group'],
                "protected": True,
                "enabled": True,
                "object": "group",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["group", "user"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "group": {
                            "_type": "uuid"
                        },
                        "user": { 
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GroupUpdate",
                "name": "Group_Update",
                "path": "group",
                "method": HTTP_PUT,
                "desc": "Update an existing API group",
                "mod": umod['group'],
                "protected": True,
                "enabled": True,
                "object": "group",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["group"],
                    "_optional": ["name", "desc", "protected"],
                    "_type": "dict",
                    "_children": {
                        "group": {
                            "_type": "uuid"
                        },
                        "name": {
                            "_type": "str"
                        },
                        "desc": {
                            "_type": "str"
                        },
                        "protected": {
                            "_type": "bool"
                        }
                    }
                }
            },
            {
                "cls": "GroupCreate",
                "name": "Group_Create",
                "path": "group",
                "method": HTTP_POST,
                "desc": "Create a new API group",
                "mod": umod['group'],
                "protected": True,
                "enabled": True,
                "object": "group",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["name", "desc", "protected"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "group": {
                            "_type": "uuid"
                        },
                        "name": {
                            "_type": "str"
                        },
                        "desc": {
                            "_type": "str"
                        },
                        "protected": {
                            "_type": "bool"
                        }
                    }
                }
            },
            {
                "cls": "GroupDelete",
                "name": "Group_Delete",
                "path": "group",
                "method": HTTP_DELETE,
                "desc": "Delete an existing API group",
                "mod": umod['group'],
                "protected": True,
                "enabled": True,
                "object": "group",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["group"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "group": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "GroupGet",
                "name": "Group_Get",
                "path": "group",
                "method": HTTP_GET,
                "desc": "Get details for an API group",
                "mod": umod['group'],
                "protected": True,
                "enabled": True,
                "object": "group",
                "object_key": "uuid",
                "rmap": {
                    "_required": [],
                    "_optional": ["group"],
                    "_type": "dict",
                    "_children": {
                        "group": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "UserEnable",
                "name": "User_Enable",
                "path": "user/enable",
                "method": HTTP_PUT,
                "desc": "Enable a user account",
                "mod": umod['user'],
                "protected": True,
                "enabled": True,
                "object": "user",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["user"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "user": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "UserDisable",
                "name": "User_Disable",
                "path": "user/disable",
                "method": HTTP_PUT,
                "desc": "Disable a user account",
                "mod": umod['user'],
                "protected": True,
                "enabled": True,
                "object": "user",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["user"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "user": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "UserResetPassword",
                "name": "User_ResetPassword",
                "path": "user/pwreset",
                "method": HTTP_PUT,
                "desc": "Reset a user's password",
                "mod": umod['user'],
                "protected": True,
                "enabled": True,
                "object": "user",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["user"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "user": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "UserDelete",
                "name": "User_Delete",
                "path": "user",
                "method": HTTP_DELETE,
                "desc": "Delete an existing API user",
                "mod": umod['user'],
                "protected": True,
                "enabled": True,
                "object": "user",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["user"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "user": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "UserCreate",
                "name": "User_Create",
                "path": "user",
                "method": HTTP_POST,
                "desc": "Create a new API user",
                "mod": umod['user'],
                "protected": True,
                "enabled": True,
                "object": "user",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["username", "group", "email", "password", "password_confirm"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "username": {
                            "_type": "str"
                        },
                        "group": {
                            "_type": "uuid"
                        },
                        "email": {
                            "_type": "str"
                        },
                        "password": {
                            "_type": "str"
                        },
                        "password_confirm": {
                            "_type": "str"    
                        }
                    }
                }
            },
            {
                "cls": "UserGet",
                "name": "User_Get",
                "path": "user",
                "method": HTTP_GET,
                "desc": "Get API user details",
                "mod": umod['user'],
                "protected": True,
                "enabled": True,
                "object": "user",
                "object_key": "uuid",
                "rmap": {
                    "_required": [],
                    "_optional": ["user"],
                    "_type": "dict",
                    "_children": {
                        "user": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "ConnectorsGet",
                "name": "Connectors_Get",
                "path": "connector",
                "method": HTTP_GET,
                "desc": "Get API connector details",
                "mod": umod['connector'],
                "protected": True,
                "enabled": True,
                "object": "connector",
                "object_key": "uuid",
                "rmap": {
                    "_required": [],
                    "_optional": ["uuid"],
                    "_type": "dict",
                    "_children": {
                        "uuid": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "ConnectorsDelete",
                "name": "Connectors_Delete",
                "path": "connector",
                "method": HTTP_DELETE,
                "desc": "Delete an existing API connector",
                "mod": umod['connector'],
                "protected": True,
                "enabled": True,
                "object": "connector",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["uuid"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "uuid": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "ConnectorsUpdate",
                "name": "Connectors_Update",
                "path": "connector",
                "method": HTTP_PUT,
                "desc": "Update an existing API connector",
                "mod": umod['connector'],
                "protected": True,
                "enabled": True,
                "object": "connector",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["uuid"],
                    "_optional": ["name", "is_oauth2", "key_file", "token_url", "auth_url"],
                    "_type": "dict",
                    "_children": {
                        "uuid": {
                            "_type": "uuid"
                        },
                        "name": {
                            "_type": "str"
                        },
                        "is_oauth2": {
                            "_type": "bool"
                        },
                        "key_file": {
                            "_type": "str"
                        },
                        "token_url": {
                            "_type": "str"
                        },
                        "auth_url": {
                            "_type": ""
                        }
                                  
                    }
                }
            },
            {
                "cls": "ConnectorsCreate",
                "name": "Connectors_Create",
                "path": "connector",
                "method": HTTP_POST,
                "desc": "Create a new API connector",
                "mod": umod['connector'],
                "protected": True,
                "enabled": True,
                "object": "connector",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["name"],
                    "_optional": ["is_oauth2", "key_file", "token_url", "auth_url"],
                    "_type": "dict",
                    "_children": {
                        "uuid": {
                            "_type": "uuid"
                        },
                        "name": {
                            "_type": "str"
                        },
                        "is_oauth2": {
                            "_type": "bool"
                        },
                        "key_file": {
                            "_type": "str"
                        },
                        "token_url": {
                            "_type": "str"
                        },
                        "auth_url": {
                            "_type": ""
                        }
                                  
                    }
                }
            },
            {
                "cls": "IntegratorsGet",
                "name": "Integrators_Get",
                "path": "integrator",
                "method": HTTP_GET,
                "desc": "Get API integrator details",
                "mod": umod['integrator'],
                "protected": True,
                "enabled": True,
                "object": "integrator",
                "object_key": "uuid",
                "rmap": {
                    "_required": [],
                    "_optional": ["uuid"],
                    "_type": "dict",
                    "_children": {
                        "uuid": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "IntegratorsDelete",
                "name": "Integrators_Delete",
                "path": "integrator",
                "method": HTTP_DELETE,
                "desc": "Delete an existing API integrator",
                "mod": umod['integrator'],
                "protected": True,
                "enabled": True,
                "object": "integrator",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["uuid"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "uuid": {
                            "_type": "uuid"
                        }
                    }
                }
            },
            {
                "cls": "IntegratorsUpdate",
                "name": "Integrators_Update",
                "path": "integrator",
                "method": HTTP_PUT,
                "desc": "Update an existing API integrator",
                "mod": umod['integrator'],
                "protected": True,
                "enabled": True,
                "object": "integrator",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["uuid"],
                    "_optional": ["name", "path", "method", "imap"],
                    "_type": "dict",
                    "_children": {
                        "uuid": {
                            "_type": "uuid"
                        },
                        "name": {
                            "_type": "str"
                        },
                        "path": {
                            "_type": "str"
                        },
                        "method": {
                            "_type": "str"
                        },
                        "imap": {
                            "_type": "str"
                        }        
                    }
                }
            },
            {
                "cls": "IntegratorsCreate",
                "name": "Integrators_Create",
                "path": "integrator",
                "method": HTTP_POST,
                "desc": "Create a new API integrator",
                "mod": umod['integrator'],
                "protected": True,
                "enabled": True,
                "object": "integrator",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["name", "path", "method", "imap"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
                        "name": {
                            "_type": "str"
                        },
                        "path": {
                            "_type": "str"
                        },
                        "method": {
                            "_type": "str"
                        },
                        "imap": {
                            "_type": "str"
                        }         
                    }
                }
            }
        ]