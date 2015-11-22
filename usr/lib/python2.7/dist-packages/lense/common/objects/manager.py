# coding=utf-8
import json
import importlib

# Django Libraries
from django.core.serializers.json import DjangoJSONEncoder

# Lense Libraries
from lense.common.objects.acl import ACLObjects

class ObjectsManager(object):
    """
    API class used to retrieve object details.
    """ 
    def _get_from_model(self, obj_type, obj_id, values={}, filters={}):
        """
        Retrieve object details directly from the model.
        
        @param obj_type: The type of object to retrieve
        @type  obj_type: str
        @param obj_id:   The ID of the object to retrieve
        @type  obj_id:   str
        @param values:   Extra parameters to pass to the values QuerySet method
        @type  values:   dict
        @param filters:  Extra filter parameters
        @type  filters:  dict
        """
        
        # Get the ACL object definition
        acl_object  = ACLObjects.get(obj_type)
        
        # Get an instance of the object class
        obj_mod     = importlib.import_module(getattr(acl_object, 'obj_mod'))
        obj_class   = getattr(obj_mod, getattr(acl_object, 'obj_cls'))
        obj_key     = getattr(acl_object, 'obj_key')
        
        # Create the object filter
        obj_filter  = {}
        
        # If retrieving a single object
        if obj_id:
            obj_filter[obj_key] = obj_id
        
        # Create the query object
        query_obj = obj_class.objects
        
        # If an object filter is defined
        if obj_filter:
            query_obj = query_obj.filter(**obj_filter)
            
        # If a values filter is defined
        if filters:
            query_obj = query_obj.filter(**filters)
        
        # If no filters were defined
        if not obj_filter and not filters:
            query_obj = query_obj.all()
        
        # Attempt to retrieve the object
        obj_details = list(query_obj.values())
        
        # Log the retrieved details
        log_data = json.dumps(obj_details, cls=DjangoJSONEncoder)
        
        # If the object doesn't exist
        if len(obj_details) == 0:
            return None
        
        # Return the object details
        if not obj_id:
            return obj_details
        return obj_details[0]
        
    def get(self, obj_type, obj_id=None, values={}, filters={}):
        """
        Retrieve details for an API object.
        
        @param obj_type: The type of object to retrieve
        @type  obj_type: str
        @param obj_id:   The ID of the object to retrieve
        @type  obj_id:   str
        @param values:   Extra parameters to pass to the values QuerySet method
        @type  values:   dict
        @param filters:  Extra filter parameters
        @type  filters:  dict
        """
        
        # If the ACL object exists
        if len(ACLObjects.get_values(obj_type)) > 0:
            return self._get_from_model(obj_type, obj_id, values=values, filters=filters)
            
        # Invalid ACL object type
        else:
            return None