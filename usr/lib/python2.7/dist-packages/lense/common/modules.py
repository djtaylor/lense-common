import re
from os import listdir
from importlib import import_module

# Lense Libraries
from lense.common.vars import HANDLERS
from lense import MODULE_ROOT, DROPIN_ROOT

class LenseModules(object):
    """
    Module helper class.
    """
    @staticmethod
    def dropin(project):
        """
        Drop-in module attributes.
        
        :param project: The target project
        :type  project: str
        """
        return {
            'client': [LenseModules._dropin_path_map('client/module'), 'lense_d.client.module']
        }.get(project, None)
    
    @staticmethod
    def builtin(project):
        """
        Built-in module attributes.
        
        :param project: The target project
        :type  project: str
        """
        return {
            'client': [LenseModules._builtin_path_map('client/module'), 'lense.client.module']
        }.get(project, None)
    
    @staticmethod
    def _dropin_path_map(rel):
        """
        Map a relative module path to the drop-in root.
        """
        return '{0}/lense_d/{1}'.format(DROPIN_ROOT, rel)
    
    @staticmethod
    def _builtin_path_map(rel):
        """
        Map a relative path to the built-in root.
        """
        return '{0}/{1}'.format(MODULE_ROOT, rel)
    
    @staticmethod
    def handlers(ext=None, load=None, args=[], kwargs={}):
        """
        Return handlers for a project.
        
        :param  ext: Handler extension (nested handlers)
        :type   ext: str
        :param load: Return instances of the handlers objects
        :type  load: str
        """
        
        # Project handler attributes / handler objects / handler extension
        handler_attrs = getattr(HANDLERS, LENSE.PROJECT.name)
        handler_objs  = {} if load else []
        
        # Scan every handler
        for handler in listdir(handler_attrs.DIR):
            
            # Ignore special files
            if re.match(r'^__.*$', handler) or re.match(r'^.*\.pyc$', handler):
                continue
            
            # Handler file path / Python path
            handler_file = '{0}/{1}{2}'.format(handler_attrs.DIR, handler, ('.py' if not ext else '/{0}.py'.format(ext)))
            handler_mod  = '{0}.{1}{2}'.format(handler_attrs.MOD, handler, ('' if not ext else '.{0}'.format(ext)))
            
            # If loading the handler objects
            if load:
                mod_obj = import_module(handler_mod)
                
                # Handler class not found
                if not hasattr(mod_obj, load):
                    handler_objs[handler] = None
            
                # If passing args/kwargs, invoke now
                if args or kwargs:
                    return getattr(mod_obj, load)(*args, **kwargs)
            
                # Load the handler class
                handler_objs[handler] = getattr(mod_obj, load)
            
            # Returning handler attributes
            else:
                handler_objs.append({
                    'name': handler,
                    'file': handler_file,
                    'mod':  handler_mod                         
                })
        
        # Return the constructed handlers object
        return handler_objs
    
    @staticmethod
    def name(file):
        """
        Extract a module name from a file path.
        """
        return re.compile(r'^([^\.]*)\..*$').sub(r'\g<1>', file)
    
    @staticmethod
    def imp(module):
        """
        Import a built-in or drop-in module.
        """
        return import_module(module)