from importlib import import_module

# Django Libraries
from django.db.models.query import QuerySet

# Lense Libraries
from lense.common.objects.utility.models import Utilities
from lense.common.objects.acl.models import ACLObjects, ACLObjectAccess, ACLGlobalAccess

class ACLKeysQuerySet(QuerySet):
    """
    Custom queryset for the ACLKeys model.
    """
    def __init__(self, *args, **kwargs):
        super(ACLKeysQuerySet, self).__init__(*args, **kwargs)
        
        # ACL object types / utilities
        self.obj_types = self._get_objects()
        self.utilities = {x['uuid']: x for x in list(Utilities.objects.all().values())}
        
    def _get_objects(self):
        """
        Construct ACL object types and definitions.
        """
        
        # Query all ACL object types
        acl_objects = list(ACLObjects.objects.all().values())
        
        # Construct and return the definition
        return {
            'types':   [x['type'] for x in acl_objects],
            'details': {x['type']: x for x in acl_objects},
        }
        
    def _extract_utilities(self, utilities):
        """
        Extract utility information from an ACL utility assignment.
        """
        
        # ACL utlities return object
        utilities_obj = []
        
        # Object type
        obj_type      = None
        
        # Construct the ACL utilities object
        for util in utilities:
            util_uuid = util['utility_id']
            utilities_obj.append({
                'uuid':   self.utilities[util_uuid]['uuid'],
                'path':   self.utilities[util_uuid]['path'],
                'desc':   self.utilities[util_uuid]['desc'],
                'method': self.utilities[util_uuid]['method'],
                'object': self.utilities[util_uuid]['object']
            })
            
            # If the object type is defined
            obj_type = obj_type if not self.utilities[util_uuid]['object'] else self.utilities[util_uuid]['object']
            
        # Return the ACL utilities object and object type
        return utilities_obj, obj_type
        
    def _extract(self, acl):
        """
        Extract and construct each ACL definition.
        """
        
        # Extract all utility access definitions
        object_util = self._extract_utilities(list(ACLObjectAccess.objects.filter(acl=acl['uuid']).values()))
        global_util = self._extract_utilities(list(ACLGlobalAccess.objects.filter(acl=acl['uuid']).values()))
        
        # Contstruct the utilities for each ACL access type
        acl['utilities'] = {
            'object': {
                'type': object_util[1],
                'list': object_util[0]
            },
            'global': {
                'type': global_util[1],
                'list': global_util[0]
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
        super(ACLKeysQuerySet, self).__init__(*args, **kwargs)
        
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
            if acl_object['type'] == 'user':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'name':  obj_details['username'],
                    'label': obj_details['email']              
                })
                
            # API group objects
            if acl_object['type'] == 'group':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'name':  obj_details['name'],
                    'label': obj_details['desc']            
                })
        
            # Utility objects
            if acl_object['type'] == 'utility':
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