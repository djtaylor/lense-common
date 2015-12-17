from importlib import import_module

# Lense Libraries
from lense.common.objects.base import LenseBaseObject

class ObjectInterface(LenseBaseObject):
    def __init__(self):
        super(ObjectInterface, self).__init__('lense.common.objects.handler.models', 'Handlers')
    
    def check_object(self, mod, cls):
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