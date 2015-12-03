from importlib import import_module

# Lense Libraries
from lense import import_class, set_arg

class Handler_Interface(object):
    
    @staticmethod
    def update(uuid, params):
        """
        Update a handler object.
        """
        handler = Handler_Interface.get(uuid)
        if not handler:
            return False
        handler.update(**params)
    
    @staticmethod
    def create(**params):
        """
        Create a new handler object.
        """
        handler = import_class('Handlers', 'lense.common.objects.handler.models', init=False)
        handler(**params).save()
        return True
    
    @staticmethod
    def check_object(mod, cls):
        """
        Make sure a handler exists and has the launch method.
        """
        # Try to import the module
        try:
            mod_inst = import_module(mod)
            
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
    
    @staticmethod
    def get(path=None, method=None, uuid=None):
        """
        Retrieve an API handler object by path and method.
        """
        handlers = import_class('Handlers', 'lense.common.objects.handler.models', init=False)
        
        # Default path / method
        path = set_arg(path, LENSE.REQUEST.path)
        method = set_arg(method, LENSE.REQUEST.method)
        
        # If the UUID is set
        if uuid:
            params = {'uuid': uuid}
        else:
            if not path and method:
                return None
            params = {
                'path': path,
                'method': method          
            }
        
        # If the handler doesn't exist
        try:
            if not handlers.objects.filter(**params).count():
                return None
            return handlers.objects.filter(**params).get()
        except:
            return None