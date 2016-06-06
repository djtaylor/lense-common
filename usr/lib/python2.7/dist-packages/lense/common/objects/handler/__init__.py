from importlib import import_module

# Lense Libraries
from lense import import_class
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
        
    def createManifest(self, handler, manifest):
        """
        Create the handler manifest.
        """
        if not self.exists(uuid=handler):
            self.log('Cannot create manifest for handler {0}, not found'.format(handler))
            return False
        
        # Get the handler
        handler = LENSE.OBJECTS.HANDLER.get_internal(uuid=handler)
        
        # Save the manifest
        model   = import_class('HandlerManifests', 'lense.common.objects.handler.models', init=False)
        model(handler=handler, manifest=manifest).save()