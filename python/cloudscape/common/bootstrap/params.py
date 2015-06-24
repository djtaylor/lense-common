from collections import OrderedDict

# cs
from cloudscape.common.utils import rstring
from cloudscape.common.vars import G_ADMIN, U_ADMIN, L_BASE
from cloudscape.common.http import HTTP_GET, HTTP_POST, HTTP_PUT, HTTP_DELETE

class _BootstrapACL(object):
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
                "acl_mod": "cloudscape.engine.api.app.gateway.models",
                "acl_cls": "DBGatewayACLGroupObjectUtilityPermissions",
                "acl_key": "utility",
                "obj_mod": "cloudscape.engine.api.app.gateway.models",
                "obj_cls": "DBGatewayUtilities",
                "obj_key": "uuid",
                "def_acl": self._get_acl_key('util.view')
            },
            {
                "type": "group",
                "name": "API Group",
                "acl_mod": "cloudscape.engine.api.app.gateway.models",
                "acl_cls": "DBGatewayACLGroupObjectGroupPermissions",
                "acl_key": "group",
                "obj_mod": "cloudscape.engine.api.app.group.models",
                "obj_cls": "DBGroupDetails",
                "obj_key": "uuid",
                "def_acl": self._get_acl_key('group.view')
            },
            {
                "type": "user",
                "name": "API User",
                "acl_mod": "cloudscape.engine.api.app.gateway.models",
                "acl_cls": "DBGatewayACLGroupObjectUserPermissions",
                "acl_key": "user",
                "obj_mod": "cloudscape.engine.api.app.user.models",
                "obj_cls": "DBUser",
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
                "type_global": True
            },
            {
                "name": "user.admin",
                "desc": "ACL for allowing global administration of users.",
                "type_object": False,
                "type_global": True
            },
            {
                "name": "user.view",
                "desc": "ACL for allowing read-only access to user objects.",
                "type_object": True,
                "type_global": False
            },
            {
                "name": "group.admin",
                "desc": "ACL for allowing global administration of groups.",
                "type_object": False,
                "type_global": True
            },
            {
                "name": "group.view",
                "desc": "ACL for allowing read-only access to group objects.",
                "type_object": True,
                "type_global": False
            },
            {
                "name": "util.admin",
                "desc": "ACL for allowing administration of API utilities.",
                "type_object": False,
                "type_global": True
            },
            {
                "name": "util.view",
                "desc": "ACL for allowing read-only access to utility objects.",
                "type_object": True,
                "type_global": False
            }
        ]

class _BootstrapInput(object):
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
                    "default": "cloudscape",
                    "prompt": "Please enter the name of the database to use/create for Cloudscape (cloudscape): ",
                    "value": None
                },
                "db_user": {
                    "type": "str",
                    "default": "cloudscape",
                    "prompt": "Please enter the name of the primary non-root database user (cloudscape): ",
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
                },
                "socket_bind_ipaddr": {
                    "type": "str",
                    "default": "127.0.0.1",
                    "prompt": "Please enter the bind IP address for the socket server (127.0.0.1): ",
                    "value": None
                }
            })             
        }
        
        # Return the prompt object
        return _prompt

class BootstrapParams(object):
    """
    Bootstrap parameters class object used to store and set the attributes
    required when using the bootstrap manager.
    """
    def __init__(self):
        
        # User input / ACL objects
        self.input  = _BootstrapInput()
        self.acl    = _BootstrapACL()
        
        # Groups/users/database/file parameters
        self.group  = self._set_group()
        self.user   = self._set_user()
        self.utils  = self._set_utils()
        self.file   = self._set_file()
        self.db     = None
    
    def get_config(self):
        """
        Load the updated server configuration
        """
        
        # Generate a new Django secret for the engine and portal
        engine_secret = "'%s'" % rstring(64)
        portal_secret = "'%s'" % rstring(64)
        
        # Return the updated server configuration
        return {
            'server': {
                'host': self.input.response.get('api_host'),
                'port': self.input.response.get('api_port'),
                'secret': engine_secret      
            },
            'db': {
                'host': self.input.response.get('db_host'),
                'port': self.input.response.get('db_port'),
                'user': self.input.response.get('db_user'),
                'password': self.input.response.get('db_user_password')
            },
            'portal': {
                'host': self.input.response.get('portal_host'),
                'port': self.input.response.get('portal_port'),
                'secret': portal_secret
            },
            'socket': {
                'host': self.input.response.get('socket_host'),
                'port': self.input.response.get('socket_port'),
                'bind_ip': self.input.response.get('socket_bind_ipaddr')
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
                'dir': '%s/dbkey' % L_BASE,
                'key': '%s/dbkey/1' % L_BASE,
                'meta': '%s/dbkey/meta' % L_BASE
            }
        }
        
        # Return the database queries
        self.db = {
            "attrs": db_attrs,
            "query": {
                "create_db": "CREATE DATABASE IF NOT EXISTS %s" % db_attrs['name'],
                "create_user": "CREATE USER '%s'@'%s' IDENTIFIED BY '%s'" % (db_attrs['user'], db_attrs['host'], db_attrs['passwd']),
                "grant_user": "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s'" % (db_attrs['name'], db_attrs['user'], db_attrs['host']),
                "flush_priv": "FLUSH PRIVILEGES"
            }
        }
    
    def _set_path(self, path):
        """
        Return a path after prepending L_BASE
        """
        return '%s/%s' % (L_BASE, path)
    
    def _set_file(self):
        """
        Set file deployment parameters.
        """
        return {
            "config": {
                "server_conf": [self._set_path("conf/default/server.conf"), self._set_path("conf/server.conf")],
                "apache_engine": [self._set_path("conf/apache/default/engine.conf"), self._set_path("conf/apache/engine.conf")],
                "apache_portal": [self._set_path("conf/apache/default/portal.conf"), self._set_path("conf/apache/portal.conf")]
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
            "password": None
        }
        
    def _set_utils(self):
        """
        Set default utility parameters
        """
        
        # Set the utility modules
        mod_gateway = 'cloudscape.engine.api.app.gateway.utils'
        mod_group   = 'cloudscape.engine.api.app.group.utils'
        mod_user    = 'cloudscape.engine.api.app.user.utils'
        
        # Return the database parameters
        return [
            {
                "cls": "GatewayTokenGet",
                "path": "gateway/token",
                "method": HTTP_GET,
                "desc": "Make a token request to the API gateway",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": "",
                "rmap": {
                    "_required": [],
                    "_optional": []
                }
            },
            {
                "cls": "GatewayACLGet",
                "path": "gateway/acl",
                "method": HTTP_GET,
                "desc": "Retrieve an ACL definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "acl",
                "object_key": "uuid",
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
                "path": "gateway/acl",
                "method": HTTP_POST,
                "desc": "Create a new ACL definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "acl",
                "object_key": "uuid",
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
                "path": "gateway/acl",
                "method": HTTP_DELETE,
                "desc": "Delete an existing ACL definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "acl",
                "object_key": "uuid",
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
                "path": "gateway/acl",
                "method": HTTP_PUT,
                "desc": "Update an existing ACL definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "acl",
                "object_key": "uuid",
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
                "path": "gateway/acl/objects",
                "method": HTTP_GET,
                "desc": "Get a listing of ACL objects",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "acl_object",
                "object_key": "type",
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
                "path": "gateway/acl/objects",
                "method": HTTP_PUT,
                "desc": "Update an ACL object definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "acl_object",
                "object_key": "type",
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
                "path": "gateway/acl/objects",
                "method": HTTP_POST,
                "desc": "Create a new ACL object definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "acl_object",
                "object_key": "type",
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
                "path": "gateway/acl/objects",
                "method": HTTP_DELETE,
                "desc": "Delete an existing ACL object definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "acl_object",
                "object_key": "uuid",
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
                "path": "gateway/utilities",
                "method": HTTP_GET,
                "desc": "Get a listing of API utilities",
                "mod": mod_gateway,
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
                "path": "gateway/utilities/open",
                "method": HTTP_PUT,
                "desc": "Open an API utility for editing",
                "mod": mod_gateway,
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
                "path": "gateway/utilities/close",
                "method": HTTP_PUT,
                "desc": "Close the editing lock on an API utility",
                "mod": mod_gateway,
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
                "path": "gateway/utilities/validate",
                "method": HTTP_PUT,
                "desc": "Validate changes to an API utility",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "utility",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["utility"],
                    "_optional": ["path", "desc", "method", "mod", "cls", "utils", "rmap", "object", "object_key", "protected", "enabled"],
                    "_type": "dict",
                    "_children": {
                        "utility": {
                            "_type": "uuid"
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
                    }
                }
            },
            {
                "cls": "GatewayUtilitiesSave",
                "path": "gateway/utilities",
                "method": HTTP_PUT,
                "desc": "Save changes to an API utility",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "utility",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["utility"],
                    "_optional": ["path", "desc", "method", "mod", "cls", "utils", "rmap", "object", "object_key", "protected", "enabled"],
                    "_type": "dict",
                    "_children": {
                        "utility": {
                            "_type": "uuid"
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
                    }
                }
            },
            {
                "cls": "GatewayUtilitiesCreate",
                "path": "gateway/utilities",
                "method": HTTP_POST,
                "desc": "Create a new API utility",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "utility",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["path", "desc", "method", "mod", "cls", "utils", "rmap", "object", "object_key", "protected", "enabled"],
                    "_optional": [],
                    "_type": "dict",
                    "_children": {
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
                    }
                }
            },
            {
                "cls": "GatewayUtilitiesDelete",
                "path": "gateway/utilities",
                "method": HTTP_DELETE,
                "desc": "Delete an existing API utility",
                "mod": mod_gateway,
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
                "path": "group/member",
                "method": HTTP_DELETE,
                "desc": "Remove a user from an API group",
                "mod": mod_group,
                "protected": True,
                "enabled": True,
                "object": "group",
                "object_key": "uuid",
                "rmap": {}
            },
            {
                "cls": "GroupMemberAdd",
                "path": "group/member",
                "method": HTTP_POST,
                "desc": "Add a user to an API group",
                "mod": mod_group,
                "protected": True,
                "enabled": True,
                "object": "group",
                "object_key": "uuid",
                "rmap": {}
            },
            {
                "cls": "GroupUpdate",
                "path": "group",
                "method": HTTP_PUT,
                "desc": "Update an existing API group",
                "mod": mod_group,
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
                "path": "group",
                "method": HTTP_POST,
                "desc": "Create a new API group",
                "mod": mod_group,
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
                "path": "group",
                "method": HTTP_DELETE,
                "desc": "Delete an existing API group",
                "mod": mod_group,
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
                "path": "group",
                "method": HTTP_GET,
                "desc": "Get details for an API group",
                "mod": mod_group,
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
                "path": "user/enable",
                "method": HTTP_PUT,
                "desc": "Enable a user account",
                "mod": mod_user,
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
                "path": "user/disable",
                "method": HTTP_PUT,
                "desc": "Disable a user account",
                "mod": mod_user,
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
                "path": "user/pwreset",
                "method": HTTP_PUT,
                "desc": "Reset a user's password",
                "mod": mod_user,
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
                "path": "user",
                "method": HTTP_DELETE,
                "desc": "Delete an existing API user",
                "mod": mod_user,
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
                "path": "user",
                "method": HTTP_POST,
                "desc": "Create a new API user",
                "mod": mod_user,
                "protected": True,
                "enabled": True,
                "object": "user",
                "object_key": "uuid",
                "rmap": {
                    "_required": ["username", "group", "email", "password", "password_confirm"],
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
                "path": "user",
                "method": HTTP_GET,
                "desc": "Get API user details",
                "mod": mod_user,
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
            }
        ]