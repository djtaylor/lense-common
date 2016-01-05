from importlib import import_module

# Django Libraries
from django.db.models.query import QuerySet

# Lense Libraries
from lense import import_class
from lense.common.objects.handler.models import Handlers

class ACLKeysQuerySet(QuerySet):
    """
    Custom queryset for the ACLKeys model.
    """
    def __init__(self, *args, **kwargs):
        super(ACLKeysQuerySet, self).__init__(*args, **kwargs)
        
        # Objects / access objects
        self.ACLObjects      = import_class('ACLObjects', 'lense.common.objects.acl.models', init=False)
        self.ACLObjectAccess = import_class('ACLAccess_Object', 'lense.common.objects.acl.models', init=False)
        self.ACLGlobalAccess = import_class('ACLAccess_Global', 'lense.common.objects.acl.models', init=False)
        
        # ACL object types / handlers
        self.obj_types = self._get_objects()
        self.handlers = {x['uuid']: x for x in list(Handlers.objects.all().values())}
        
    def _get_objects(self):
        """
        Construct ACL object types and definitions.
        """
        
        # Query all ACL object types
        acl_objects = list(self.ACLObjects.objects.all().values())
        
        # Construct and return the definition
        return {
            'types':   [x['object_type'] for x in acl_objects],
            'details': {x['object_type']: x for x in acl_objects},
        }
        
    def _extract_handlers(self, handlers):
        """
        Extract handler information from an ACL handler assignment.
        """
        
        # ACL handlers return object
        handlers_obj = []
        
        # Object type
        obj_type      = None
        
        # Construct the ACL handlers object
        for handler in handlers:
            handler_uuid = handler['handler_id']
            handlers_obj.append({
                'uuid':   self.handlers[handler_uuid]['uuid'],
                'path':   self.handlers[handler_uuid]['path'],
                'desc':   self.handlers[handler_uuid]['desc'],
                'method': self.handlers[handler_uuid]['method'],
                'object': self.handlers[handler_uuid]['object']
            })
            
            # If the object type is defined
            obj_type = obj_type if not self.handlers[handler_uuid]['object'] else self.handlers[handler_uuid]['object']
            
        # Return the ACL handlers object and object type
        return handlers_obj, obj_type
        
    def _extract(self, acl):
        """
        Extract and construct each ACL definition.
        """
        
        # Extract all handler access definitions
        object_handler = self._extract_handlers(list(self.ACLObjectAccess.objects.filter(acl=acl['uuid']).values()))
        global_handler = self._extract_handlers(list(self.ACLGlobalAccess.objects.filter(acl=acl['uuid']).values()))
        
        # Contstruct the handlers for each ACL access type
        acl['handlers'] = {
            'object': {
                'type': object_handler[1],
                'list': object_handler[0]
            },
            'global': {
                'type': global_handler[1],
                'list': global_handler[0]
            }          
        }
        
        # Return the constructed ACL object
        return acl
        
    def values(self, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Store the initial results
        _r = super(ACLKeysQuerySet, self).values(*fields)
        
        # ACL return object
        _a = []
        
        # Process each ACL definition
        for acl in _r:
            _a.append(self._extract(acl))
        
        # Return the constructed ACL results
        return _a

class ACLObjectsQuerySet(QuerySet):
    """
    Custom queryset for the ACLObjects model.
    """
    def __init__(self, *args, **kwargs):
        super(ACLObjectsQuerySet, self).__init__(*args, **kwargs)
        
        # Detailed object list
        self._detailed = False
        
    def _extract(self, acl_object):
        """
        Extract object details.
        """
           
        # If not extracting object details
        if not self._detailed:
            return acl_object
            
        # Get an instance of the object class
        obj_mod   = import_module(acl_object['obj_mod'])
        obj_class = getattr(obj_mod, acl_object['obj_cls'])
        obj_key   = acl_object['obj_key']
        
        # Define the detailed objects container
        acl_object['objects'] = []
        for obj_details in list(obj_class.objects.all().values()):
                
            # API user objects
            if acl_object['object_type'] == 'user':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'name':  obj_details['username'],
                    'label': obj_details['email']              
                })
                
            # API group objects
            if acl_object['object_type'] == 'group':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'name':  obj_details['name'],
                    'label': obj_details['desc']            
                })
        
            # Handler objects
            if acl_object['object_type'] == 'handler':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'path':  obj_details['path'],
                    'label': '{0}:{1}'.format(obj_details['method'], obj_details['path'])
                })
        
        # Return the detailed ACL object
        return acl_object
        
    def values(self, detailed=False, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Set the detailed results flag
        self._detailed = detailed
        
        # Store the initial results
        _r = super(ACLObjectsQuerySet, self).values(*fields)
        
        # ACL return object
        _a = []
        
        # Process each ACL object definition
        for acl_object in _r:
            _a.append(self._extract(acl_object))
        
        # Return the constructed ACL results
        return _a