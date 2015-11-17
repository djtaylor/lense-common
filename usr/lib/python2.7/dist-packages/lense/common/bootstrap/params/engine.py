from collections import OrderedDict

# Lense Libraries
from lense.common.utils import rstring
from lense.common.vars import GROUPS, USERS, DB_ENCRYPT_DIR
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
                "acl_mod": "lense.common.objects.acl.models",
                "acl_cls": "ACLGroupPermissions_Object_Utility",
                "acl_key": "utility",
                "obj_mod": "lense.common.objects.utility.models",
                "obj_cls": "Utilities",
                "obj_key": "uuid",
                "def_acl": self._get_acl_key('util.view')
            },
            {
                "type": "group",
                "name": "API Group",
                "acl_mod": "lense.common.objects.acl.models",
                "acl_cls": "ACLGroupPermissions_Object_Group",
                "acl_key": "group",
                "obj_mod": "lense.common.objects.group.models",
                "obj_cls": "APIGroups",
                "obj_key": "uuid",
                "def_acl": self._get_acl_key('group.view')
            },
            {
                "type": "user",
                "name": "API User",
                "acl_mod": "lense.common.objects.acl.models",
                "acl_cls": "ACLGroupPermissions_Object_User",
                "acl_key": "user",
                "obj_mod": "lense.common.objects.user.models",
                "obj_cls": "APIUser",
                "obj_key": "uuid",
                "def_acl": self._get_acl_key('user.view')
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
                    "Token_Get"
                ]
            },
            {
                "name": "user.admin",
                "desc": "ACL for allowing global administration of users.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "User_Get",
                    "User_Create",
                    "User_Delete",
                    "User_Enable",
                    "User_Disable",
                    "User_ResetPassword"
                ]
            },
            {
                "name": "user.view",
                "desc": "ACL for allowing read-only access to user objects.",
                "type_object": True,
                "type_global": False,
                "util_classes": [
                    "User_Get"
                ]
            },
            {
                "name": "group.admin",
                "desc": "ACL for allowing global administration of groups.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "Group_Get",
                    "Group_Create",
                    "Group_Update",
                    "Group_Delete",
                    "GroupMember_Add",
                    "GroupMember_Remove"
                ]
            },
            {
                "name": "group.view",
                "desc": "ACL for allowing read-only access to group objects.",
                "type_object": True,
                "type_global": False,
                "util_classes": [
                    "Group_Get"
                ]
            },
            {
                "name": "util.admin",
                "desc": "ACL for allowing administration of API utilities.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "Utility_Get",
                    "Utility_Create",
                    "Utility_Save",
                    "Utility_Validate",
                    "Utility_Delete",
                    "Utility_Close",
                    "Utility_Open"
                ]
            },
            {
                "name": "util.view",
                "desc": "ACL for allowing read-only access to utility objects.",
                "type_object": True,
                "type_global": False,
                "util_classes": [
                    "Utility_Get"
                ]
            },
            {
                "name": "acl.view",
                "desc": "ACL for allowing read-only access to ACL definitions.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                     "ACL_Get"            
                ]
            },
            {
                "name": "acl.admin",
                "desc": "ACL for allowing administration of ACL definitions.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                     "ACL_Get",
                     "ACL_Create",
                     "ACL_Delete",
                     "ACL_Update"       
                ]
            },
            {
                "name": "acl_object.view",
                "desc": "ACL for allowing read-only access to ACL object definitions.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "ACLObjects_Get"
                ]
            },
            {
                "name": "acl_object.admin",
                "desc": "ACL for allowing administration of ACL object definitions.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "ACLObjects_Get",
                    "ACLObjects_Create",
                    "ACLObjects_Delete",
                    "ACLObjects_Update"
                ]
            },
            {
                "name": "stats.admin",
                "desc": "ACL for allowing administration of API statistics.",
                "type_object": False,
                "type_global": True,
                "util_classes": [
                    "StatsRequest_Get"
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
                },
                "api_service_email": {
                    "type": "str",
                    "default": None,
                    "prompt": "Please enter the email address for the default service account: ",
                    "value": None  
                },
                "api_service_password": {
                    "type": "pass",
                    "default": None,
                    "prompt": "Please enter a password for the default service account: ",
                    "value": None
                },
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
        self.groups = self._set_groups()
        self.users  = self._set_users()
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
        
    def _set_utils(self):
        """
        Set default utility parameters
        """
        
        # Set the utility handlers
        umod = {
            'acl':     'lense.engine.api.handlers.acl',
            'group':   'lense.engine.api.handlers.group',
            'user':    'lense.engine.api.handlers.user',
            'stats':   'lense.engine.api.handlers.stats',
            'utility': 'lense.engine.api.handlers.utility',
            'token':   'lense.engine.api.handlers.token'
        }
        
        
        # Return the database parameters
        return [
            {
                "cls": "Token_Get",
                "name": "Token_Get",
                "path": "token",
                "method": HTTP_GET,
                "desc": "Make an API token request",
                "mod": umod['token'],
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
                "cls": "ACL_Get",
                "name": "ACL_Get",
                "path": "acl",
                "method": HTTP_GET,
                "desc": "Retrieve an ACL definition",
                "mod": umod['acl'],
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
                "cls": "ACL_Create",
                "name": "ACL_Create",
                "path": "acl",
                "method": HTTP_POST,
                "desc": "Create a new ACL definition",
                "mod": umod['acl'],
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
                "cls": "ACL_Delete",
                "name": "ACL_Delete",
                "path": "acl",
                "method": HTTP_DELETE,
                "desc": "Delete an existing ACL definition",
                "mod": umod['acl'],
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
                "cls": "ACL_Update",
                "name": "ACL_Update",
                "path": "acl",
                "method": HTTP_PUT,
                "desc": "Update an existing ACL definition",
                "mod": umod['acl'],
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
                "cls": "ACLObjects_Get",
                "name": "ACLObjects_Get",
                "path": "acl/objects",
                "method": HTTP_GET,
                "desc": "Get a listing of ACL objects",
                "mod": umod['acl'],
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
                "cls": "ACLObjects_Update",
                "name": "ACLObjects_Update",
                "path": "acl/objects",
                "method": HTTP_PUT,
                "desc": "Update an ACL object definition",
                "mod": umod['acl'],
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
                "cls": "ACLObjects_Create",
                "name": "ACLObjects_Create",
                "path": "acl/objects",
                "method": HTTP_POST,
                "desc": "Create a new ACL object definition",
                "mod": umod['acl'],
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
                "cls": "ACLObjects_Delete",
                "name": "ACLObjects_Delete",
                "path": "acl/objects",
                "method": HTTP_DELETE,
                "desc": "Delete an existing ACL object definition",
                "mod": umod['acl'],
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
                "cls": "Utility_Get",
                "name": "Utility_Get",
                "path": "utility",
                "method": HTTP_GET,
                "desc": "Get a listing of API utilities",
                "mod": umod['utility'],
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
                "cls": "Utility_Open",
                "name": "Utility_Open",
                "path": "utility/open",
                "method": HTTP_PUT,
                "desc": "Open an API utility for editing",
                "mod": umod['utility'],
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
                "cls": "Utility_Close",
                "name": "Utility_Close",
                "path": "utility/close",
                "method": HTTP_PUT,
                "desc": "Close the editing lock on an API utility",
                "mod": umod['utility'],
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
                "cls": "Utility_Validate",
                "name": "Utility_Validate",
                "path": "utility/validate",
                "method": HTTP_PUT,
                "desc": "Validate changes to an API utility",
                "mod": umod['utility'],
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
                "cls": "Utility_Save",
                "name": "Utility_Save",
                "path": "utility",
                "method": HTTP_PUT,
                "desc": "Save changes to an API utility",
                "mod": umod['utility'],
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
                "cls": "Utility_Create",
                "name": "Utility_Create",
                "path": "utility",
                "method": HTTP_POST,
                "desc": "Create a new API utility",
                "mod": umod['utility'],
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
                "cls": "Utility_Delete",
                "name": "Utility_Delete",
                "path": "utility",
                "method": HTTP_DELETE,
                "desc": "Delete an existing API utility",
                "mod": umod['utility'],
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
                "cls": "GroupMember_Remove",
                "name": "GroupMember_Remove",
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
                "cls": "GroupMember_Add",
                "name": "GroupMember_Add",
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
                "cls": "Group_Update",
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
                "cls": "Group_Create",
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
                "cls": "Group_Delete",
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
                "cls": "Group_Get",
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
                "cls": "User_Enable",
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
                "cls": "User_Disable",
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
                "cls": "User_ResetPassword",
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
                "cls": "User_Delete",
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
                "cls": "User_Create",
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
                "cls": "User_Get",
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
                "cls": "StatsRequest_Get",
                "name": "StatsRequest_Get",
                "path": "stats/request",
                "method": HTTP_GET,
                "desc": "Get API request statistics",
                "mod": umod['stats'],
                "protected": True,
                "enabled": True,
                "object": None,
                "object_key": None,
                "rmap": {
                    "_required": [],
                    "_optional": [
                        "path", "method", "client_ip", "client_user", "client_group", "endpoint", "user_agent", "retcode", "req_size", "rsp_size", "rsp_time_ms", "from", "to"
                    ],
                    "_type": "dict",
                    "_children": {
                        "path": {
                            "_type": "str"
                        },
                        "method": {
                            "_type": "str"
                        },
                        "client_ip": {
                            "_type": "str"
                        },
                        "client_user": {
                            "_type": "str"
                        },
                        "client_group": {
                            "_type": "str"
                        },
                        "endpoint": {
                            "_type": "str"
                        },
                        "user_agent": {
                            "_type": "str"
                        },
                        "retcode": {
                            "_type": "str"
                        },
                        "req_size": {
                            "_type": "str"
                        },
                        "rsp_size": {
                            "_type": "str"
                        },
                        "rsp_time_ms": {
                            "_type": "str"
                        },
                        "from": {
                            "_type": "str"
                        },
                        "to": {
                            "_type": "str"
                        }
                    }
                }
            }
        ]