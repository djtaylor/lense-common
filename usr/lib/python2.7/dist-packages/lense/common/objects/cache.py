# coding=utf-8
import sys
import json
import base64
import hashlib
import importlib

# Django Libraries
from django.core.serializers.json import DjangoJSONEncoder

# Lense Libraries
from lense.common import config
from lense.common import logger
from lense.common.objects.acl import ACLObjects

class CacheManager(object):
    """
    API class responsible for caching database queries.
    """
    def __init__(self):
        
        # Configuration / logger objects
        self.conf = config.parse('ENGINE')
        self.log  = logger.create(__name__, self.conf.utils.log)
        
    def get_object(self, obj_type, obj_id=None, decode=True, filters={}):
        """
        Retrieve cached data for an object in the database.
        """
        
        # Object filter parameters
        obj_filter = {
            'object_type': obj_type
        }
        
        # If retrieving a single object
        if obj_id:
            obj_filter['object_id'] = obj_id
        self.log.info('No cached data for object <{}> of type <{}> found'.format(obj_id, obj_type))
        
        # Return empty data
        return False
        
    def save_object(self, obj_type, obj_id, values={}):
        """
        Save cache data for an object in the database.
        """
    
        # If the ACL object exists
        if len(ACLObjects.get_values(obj_type)) > 0:
            try:
                
                # If supplied, values argument must be a dictionary
                if values and not isinstance(values, dict):
                    self.log.error('Failed to cache object <{}> of type <{}>, values keyword must contain a dictionary'.format(obj_id, obj_type))
                    return False
                
                # Get the ACL object definition
                acl_object = ACLObjects.get(type=obj_type)
        
                # Get an instance of the object class
                obj_mod    = importlib.import_module(getattr(acl_object, 'obj_mod'))
                obj_class  = getattr(obj_mod, getattr(acl_object, 'obj_cls'))
                obj_key    = getattr(acl_object, 'obj_key')
                
                # Create the object filter
                obj_filter = {}
                obj_filter[obj_key] = obj_id
                
                # Define the cache object filter
                cache_filter = {
                    'object_type': obj_type,
                    'object_id':   obj_id
                }
                
                # If the object doesn't exist anymore
                if not obj_class.objects.filter(**obj_filter).count():
                    
                    # If an expired cache entry exists
                    if DBClusterCache.objects.filter(**cache_filter).count():
                        self.log.info('Base object <{}> of type <{}> no longer exists, flushing cached entry'.format(obj_id, obj_type))
                        
                        # Flush the old cache entry
                        DBClusterCache.objects.filter(**cache_filter).delete()
                        
                    # Expired cache object cleared
                    return True
                
                # Get the object details
                obj_details = base64.encodestring(json.dumps(list(obj_class.objects.filter(**obj_filter).values(**values))[0], cls=DjangoJSONEncoder))
                obj_size    = sys.getsizeof(obj_details)
                obj_hash    = hashlib.md5(obj_details).hexdigest()
                
                # If the object already has a cache entry
                if DBClusterCache.objects.filter(**cache_filter).count():
                    
                    # Get the current cache entry
                    cache_row = list(DBClusterCache.objects.filter(**cache_filter).values())[0]
                    
                    # If the cached data hasn't changed
                    if cache_row['object_hash'] == obj_hash:
                        return self.log.info('Cached data unchanged for object <{}> of type <{}>'.format(obj_id, obj_type))
                    
                    # Update the cached data
                    DBClusterCache.objects.filter(**cache_filter).update(object_data=obj_details, object_size=obj_size)
                    
                # Create a new cache entry
                else:
                
                    # Create the cache entry
                    DBClusterCache(
                        object_type = acl_object,
                        object_id   = obj_id,
                        object_data = obj_details,
                        object_hash = obj_hash,
                        object_size = obj_size
                    ).save()
                
                # Object successfull cached
                self.log.info('Cached data for object <{}> of type <{}>: bytes_cached={}, hash={}'.format(obj_id, obj_type, str(obj_size), obj_hash))
                
            # Critical error when caching object
            except Exception as e:
                self.log.exception('Failed to cache object <{}> of type <{}>: {}'.format(obj_id, obj_type, str(e)))
            
        # ACL object does not exist
        else:
            self.log.error('Cannot cache object <{}> of type <{}>, ACL object type not found'.format(obj_id, obj_type))
    
    def flush_object(self, obj_type, obj_id):
        """
        Flush the cache entry for a specific object from the database.
        """
        
        # Filter parameters
        filter = {
            'object_type': obj_type,
            'object_id':   obj_id
        }
        
        # If the object exists
        if DBClusterCache.objects.filter(**filter).count():
            
            # Delete the object cache entry
            DBClusterCache.objects.filter(**filter).delete()
            
            # Successfully flushed object cache
            self.log.info('Successfully flushed cache for object <{}> of type <{}>'.format(obj_id, obj_type))
            
        # Object does not exist
        else:
            self.log.error('Failed to flush cache for object <{}> of type <{}>, cache entry not found'.format(obj_id, obj_type))
            
    def flush_all(self):
        """
        Flush the entire cache table.
        """
        DBClusterCache.objects.all().delete()