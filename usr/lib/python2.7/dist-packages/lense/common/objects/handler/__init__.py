from json import loads
from importlib import import_module

# Lense Libraries
from lense import import_class
from lense.common.objects.base import LenseBaseObject

class ObjectInterface(LenseBaseObject):
    def __init__(self):
        super(ObjectInterface, self).__init__('lense.common.objects.handler.models', 'Handlers')
    
        # Manifests model
        self.manifest = import_class('HandlerManifests', 'lense.common.objects.handler.models', init=False)
    
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
    
    def extend(self, handler):
        """
        Construct extended handler attributes.
        
        :param user: The handler object to extend
        :type  user: APIHandler
        :rtype: APIHandler
        """
        uuid = LENSE.OBJECTS.getattr(handler, 'uuid')
        
        # Extend the handler object
        for k,v in {
            'manifest': self.get_manifest(uuid)
        }.iteritems():
            self.log('Extending handler {0} attributes -> {1}={2}'.format(uuid,k,v), level='debug', method='extend')
            LENSE.OBJECTS.setattr(handler, k, v)
        return handler
    
    def get_manifest(self, handler):
        """
        Return a handler's manifest contents.
        """
        try:
            return loads(self.manifest.objects.get(handler=handler).json)
        except:
            return None
    
    def create_manifest(self, handler, manifest):
        """
        Create the handler manifest.
        """
        LENSE.ensure(isinstance(handler, self.model),
            value = True,
            code  = 400,
            error = 'Must be an instance of Handlers, not: {0}'.format(type(handler)))
        
        # Save the manifest
        self.manifest(handler=handler, json=manifest).save()
    
    def get(self, **kwargs):
        """
        Retrieve handler object(s)
        """
        handler = super(ObjectInterface, self).get(**kwargs)
        
        # No handler found
        if not handler:
            return None
        
        # Multiple handler objects
        if isinstance(handler, list):
            for h in handler:
                self.extend(h)
            return handler
        
        # Single handler object
        return self.extend(handler)
    
    def create(self, **kwargs):
        """
        Create a new handler object.
        """
        
        # UUID / manifest
        uuid     = LENSE.extract(kwargs, 'uuid', delete=False, default=LENSE.uuid4())
        manifest = LENSE.extract(kwargs, 'manifest', default=None)

        # Multiple handlers cannot use the same path/method
        LENSE.ensure(self.exists(path=kwargs['path'], method=kwargs['method']),
            value = False,
            code  = 400,
            error = 'Cannot create duplication handler for: {0}@{1}'.format(kwargs['method'], kwargs['path']))
        
        # Cannot duplicate UUID
        LENSE.ensure(self.exists(uuid=uuid),
            value = False,
            code  = 400,
            error = 'Cannot create duplicate handler for: {0}'.format(uuid))
        
        # Create the handler
        handler = super(ObjectInterface, self).create(**kwargs)
        
        # Create an associated manifest
        self.create_manifest(handler, manifest)
        
        # Get and return the new handler object
        return self.get(uuid=uuid)