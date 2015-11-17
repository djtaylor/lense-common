# coding=utf-8
import json
import importlib

# Django Libraries
from django.core.serializers.json import DjangoJSONEncoder

# Lense Libraries
from lense.common import config
from lense.common import logger
from lense.common.objects.acl import ACLObjects
from lense.common.objects.cache import CacheManager

class ObjectsManager(object):
    """
    API class used to retrieve object details. If cache retrieval is enabled, the
    object details will be pulled from the database cache table.
    """
    def __init__(self):
        
        # Configuration / logger objects
        self.conf  = config.parse('ENGINE')
        self.log   = logger.create(__name__, self.conf.utils.log)
        
        # Cache manager
        self.cache = CacheManager()
        
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
        self.log.info('Retrieving object data from model: type={}, id={}'.format(obj_type, repr(obj_id)))
        
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
            self.log.info('Applying object filters: {}'.format(json.dumps(obj_filter)))
            query_obj = query_obj.filter(**obj_filter)
            
        # If a values filter is defined
        if filters:
            self.log.info('Applying value filters: {}'.format(json.dumps(filters)))
            query_obj = query_obj.filter(**filters)
        
        # If no filters were defined
        if not obj_filter and not filters:
            self.log.info('No filters defined, retrieving all objects')
            query_obj = query_obj.all()
        
        # Log the constructed query object
        self.log.info('Constructed object query: {}'.format(str(query_obj)))
        
        # Attempt to retrieve the object
        obj_details = list(query_obj.values())
        
        # Log the retrieved details
        log_data = json.dumps(obj_details, cls=DjangoJSONEncoder)
        self.log.info('Retrieved object details: length={}, data={}'.format(len(log_data), (log_data[:75] + '...') if len(log_data) > 75 else log_data))
        
        # If the object doesn't exist
        if len(obj_details) == 0:
            return None
        
        # Return the object details
        if not obj_id:
            return obj_details
        return obj_details[0]
        
    def get(self, obj_type, obj_id=None, cache=True, values={}, filters={}):
        """
        Retrieve details for an API object.
        
        @param obj_type: The type of object to retrieve
        @type  obj_type: str
        @param obj_id:   The ID of the object to retrieve
        @type  obj_id:   str
        @param cache:    Enable or disable retrieval from the database cache table
        @type  cache:    bool
        @param values:   Extra parameters to pass to the values QuerySet method
        @type  values:   dict
        @param filters:  Extra filter parameters
        @type  filters:  dict
        """
        
        # If the ACL object exists
        if len(ACLObjects.get_values(obj_type)) > 0:
            self.log.info('Retrieving database object: type={}, id={}, cache={}'.format(obj_type, repr(obj_id), repr(cache)))
            
            # If retrieving from the database cache table and caching not explicitly disabled
            if cache and not (self.conf.engine.caching == False):
            
                # Look for object details in the cache
                cached_obj = self.cache.get_object(obj_type, obj_id, filters=filters)
                
                # If cached data found
                if cached_obj:
                    self.log.info('Cached data found for object: type={}, id={}'.format(obj_type, repr(obj_id)))
                    return cached_obj
                
                # No cached data found, retrieve directly from the object model
                return self._get_from_model(obj_type, obj_id, values=values, filters=filters)
                
            # If querying directly from the database
            else:
                return self._get_from_model(obj_type, obj_id, values=values, filters=filters)
            
        # Invalid ACL object type
        else:
            self.log.error('Failed to retrieve object <{}> of type <{}>, object type not found'.format(obj_id, obj_type))
            
            # Return an empty result
            return None