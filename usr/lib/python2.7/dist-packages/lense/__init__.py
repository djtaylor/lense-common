from os.path import dirname, abspath
from sys import stderr, exit
from importlib import import_module

# Module root / drop-in root
MODULE_ROOT = dirname(abspath(__file__))
DROPIN_ROOT = '/usr/share/lense/python'

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
            exit(1)
        
    except Exception as e:
        stderr.write('Failed to import <{0}> from <{1}>: {2}\n'.format(cls, mod, str(e)))
        exit(1)