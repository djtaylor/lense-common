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
            manifest = loads(self.manifest.objects.get(handler=handler).json)
            self.log('Retrieved manifest for handler: {0}'.format(handler), level='info', method='get_manifest')
            return manifest
        except:
            self.log('Handler has no manifest: {0}'.format(handler.uuid), level='info', method='get_manifest')
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
        self.log('Created manifest for handler: {0}'.format(handler.uuid), level='info', method='create_manifest')
    
    def update_manifest(self, handler, manifest):
        """
        Update a handler manifest.
        """
        LENSE.ensure(isinstance(handler, self.model),
            value = True,
            code  = 400,
            error = 'Must be an instance of Handlers, not: {0}'.format(type(handler)))
    
        # Get the manifest
        manifest_object = self.manifest(handler=handler.uuid)
        manifest_object.json = manifest
        manifest_object.save()
        self.log('Updated manifest for handler: {0}'.format(handler.uuid), level='info', method='update_manifest')
    
    def open(self, **kwargs):
        """
        Open a handler for editing.
        """
        uuid = LENSE.extract(kwargs, 'uuid')
    
        # Make sure the handler exists
        handler = LENSE.ensure(self.get(uuid=uuid), 
            isnot = None, 
            error = 'Could not find handler: {0}'.format(uuid),
            debug = 'Handler {0} exists, retrieved object'.format(uuid),
            code  = 404)

        # Check if the handler is locked
        if handler.locked == True:
            LENSE.ensure(handler.locked_by,
                value = LENSE.REQUEST.USER.name,
                error = 'Could not open handler {0}, already checked out by {1}'.format(handler.uuid, handler.locked_by),
                code  = 400)
            return True
        
        # Update the lock attributes
        LENSE.ensure(self.update(handler, **{
            'locked': True,
            'locked_by': LENSE.REQUEST.USER.name
        }), error = 'Failed to check out handler {0}'.format(uuid),
            log   = 'Checking out hander {0}: locked=True'.format(uuid))
        
    def close(self, **kwargs):
        """
        Close a handler edit lock.
        """
        uuid = LENSE.extract(kwargs, 'uuid')
    
        # Make sure the handler exists
        handler = LENSE.ensure(self.get(uuid=uuid), 
            isnot = None, 
            error = 'Could not find handler: {0}'.format(uuid),
            debug = 'Handler {0} exists, retrieved object'.format(uuid),
            code  = 404)
        
        # Check if the handler is already close
        if not handler.locked:
            return True
            
        # Update the lock attributes
        LENSE.ensure(self.update(handler, **{
            'locked': False,
            'locked_by': None
        }), error = 'Failed to check in handler {0}'.format(uuid),
            log   = 'Checking in hander {0}: locked=False'.format(uuid))
    
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
        uuid     = LENSE.extract(kwargs, 'uuid', delete=False, default=LENSE.uuid4(), store=True)
        manifest = LENSE.extract(kwargs, 'manifest')

        # Multiple handlers cannot use the same path/method
        LENSE.ensure(self.exists(path=kwargs['path'], method=kwargs['method']),
            value = False,
            code  = 400,
            error = 'Cannot create duplicate handler for: {0}@{1}'.format(kwargs['method'], kwargs['path']))
        
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
        return self.get(uuid=handler.uuid)
    
    def update(self, **kwargs):
        """
        Update a handler object.
        """
        uuid = LENSE.extract(kwargs, 'uuid')
        
        # Updating the manifest
        manifest = LENSE.extract(kwargs, 'manifest', default=None)
        
        # Get the handler
        handler = LENSE.ensure(super(ObjectInterface, self).get(uuid=uuid),
            isnot = None,
            error = 'Could not find handler',
            code  = 404)
        
        # Update the manifest
        if manifest:
            self.update_manifest(handler, manifest)
        
        # Update the user
        super(ObjectInterface, self).update(handler, **kwargs)
        
        # Get and return the updated user
        return self.get(uuid=uuid)
    
    def delete(self, **kwargs):
        """
        Delete a handler object.
        """
        uuid = LENSE.extract(kwargs, 'uuid')
        
        # Look for the handler
        handler = LENSE.ensure(self.get(uuid=target), 
            isnot = None, 
            error = 'Could not find handler: {0}'.format(uuid),
            debug = 'Handler {0} exists, retrieved object'.format(uuid),
            code  = 404)
        
        # Make sure the handler isn't protected
        LENSE.ensure(handler.protected, 
            value = False, 
            error = 'Cannot delete a protected handler', 
            debug = 'Handler is protected: {0}'.format(repr(handler.protected)),
            code  = 403)
        
        # Make sure the handler isn't locked
        LENSE.ensure(handler.locked,
            value = False,
            error = 'Cannot delete handler, locked by: {0}'.format(handler.locked_by),
            code  = 403)
        
        # Delete the handler
        LENSE.ensure(handler.delete(),
            error = 'Failed to delete the handler: {0}'.format(uuid),
            log   = 'Deleted handler {0}'.format(uuid),
            code  = 500)
        
    def list(self):
        """
        Method for doing an unprivileged list of handlers.
        """
        handlers = {}
        
        # Construct available handlers
        for h in self.get_internal():
            handlers[h.name] = {
                'uuid': h.uuid,
                'path': h.path,
                'method': h.method,
                'name': h.name,
                'desc': h.desc              
            }
        return handlers