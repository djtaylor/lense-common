import re
from os import listdir
from sys import exc_info
from sys import stderr, exit
from traceback import print_exc
from importlib import import_module
from os.path import dirname, abspath, isdir

# Module root / drop-in root
MODULE_ROOT = dirname(abspath(__file__))
DROPIN_ROOT = '/usr/share/lense/python'

def set_arg(default, alt):
    """
    Set the value of an argument.
    
    :param default: The default attribute to check for
    :type  default: str
    :param     alt: An alternate attribute to set
    :type      alt: str
    :rtype: str|None
    """
    return default if default else alt

def get_applications(defaults=[], by_name=False):
    """
    Return a tuple of available applications.
    
    :param defaults: Default Django applications to load
    :type  defaults: list
    :rtype: tuple
    """
    
    # Applications root
    APPS_ROOT = '{0}/common/objects'.format(MODULE_ROOT)
    
    # Get all applications
    for app in listdir(APPS_ROOT):
        
        # Ignore special and binary files
        if re.match(r'^__.*$', app) or re.match(r'^.*\.pyc$', app):
            continue
        
        # Look for application directories
        if isdir('{0}/{1}'.format(APPS_ROOT, app)):
            
            # If loading by name
            if by_name:
                defaults.append([app, 'lense.common.objects.{0}'.format(app)])
            
            # Load by application path only
            else:
                defaults.append('lense.common.objects.{0}'.format(app))
    
    # Return available applications
    return tuple(defaults)

def import_class(cls, mod, init=True, ensure=True, args=[], kwargs={}):
    """
    Import a module, create an instance of a class, and pass optional arguments.
    
    :param cls:    Class name to import
    :type  cls:    str
    :param module: Class module source
    :type  module: str
    :param init:   Initialize the class object or not
    :type  init:   bool
    :rtype: object
    """
    try:
        if not ensure:
            return None
        
        # Import the module and class pointer
        mod_obj = import_module(mod)
        mod_cls = getattr(mod_obj, cls)
        
        # Create the class
        try:
            if init:
                return mod_cls(*args, **kwargs)
            return mod_cls
                
        # Class creation failed
        except Exception as e:
            stderr.write('Failed to create <{0}>: {1}\n'.format(cls, str(e)))
            print_exc()
            exit(1)
        
    except Exception as e:
        stderr.write('Failed to import <{0}> from <{1}>: {2}\n'.format(cls, mod, str(e)))
        print_exc()
        exit(1)