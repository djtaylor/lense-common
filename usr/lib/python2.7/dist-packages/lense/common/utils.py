from __future__ import print_function
import sys
import string
import random
from os import geteuid

def ensure_root():
    """
    Make sure the current process is being run as root or with sudo privileges.
    """
    if not geteuid() == 0:
        print('ERROR: This script must be run as root or with sudo privileges')
        sys.exit(1)

def set_response(rsp_obj, default):
    """
    Convenience method for returning a default value if the queried utility has no return values.
    """
    return default if not rsp_obj else rsp_obj

def truncate(string, length=75):
    """
    Return a truncated string.
    """
    return (string[:75] + '...') if len(string) > 75 else string

def rstring(length=12):
    """
    Helper method used to generate a random string.
    """
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(length)])

def autoquote(v):
    """
    Autoquote a return value. If the value is a string, quote and return. If the
    object is a type of number, do not quote. If the object is boolean or an
    object, return a representation.
    """
    
    # Int / Float / Long / Complex
    if (isinstance(v, int)) or (isinstance(v, float)) or (isinstance(v, long)) or (isinstance(v, complex)):
        return v
    
    # True / False / None / List / Dictionary
    elif (v == None) or (v == False) or (v == True) or (isinstance(v, list)) or (isinstance(v, dict)):
        return repr(v)
    
    # String / Unicode / etc.
    else:
        return '[%s]' % v

def mod_has_class(mod, cls, no_launch=False):
    """
    Helper method used to check if a module file contains a class definition.
    
    :param mod: The path to the module to inspect
    :type mod: str
    :param cls: The class definition name
    :type cls: str
    """

    # Try to import the module
    try:
        mod_inst = importlib.import_module(mod)
        
        # Make sure the module has the class definition
        if not hasattr(mod_inst, cls):
            return False
        
        # Create an instance of the class
        cls_inst = getattr(mod_inst, cls)
        if not no_launch:
            if not hasattr(cls_inst, 'launch') or not callable(cls_inst.launch):
                return False
        return False
    except Exception as e:
        return False
