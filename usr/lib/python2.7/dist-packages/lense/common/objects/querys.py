import sys
import json
from copy import copy

# Django Libraries
from django.db import models

class APIExtractor(object):
    """
    Class object used to extract values from the database internal to the
    APIQuerySet object.
    """
    def __init__(self):
        
        # Object manager
        self._objects = ObjectsManager()
    
        # Cached data / filters / values
        self._cache   = True
        self._filters = None
        self._values  = None
    
    def _get(self, obj_type, obj_id=None):
        """
        Worker method for retrieving API objects.
        """
        return LENSE.OBJECTS.get(obj_type=obj_type, obj_id=obj_id, cache=self._cache, filters=self._filters, values=self._values)
    
    def values(self, values=None):
        """
        Set an query values.
        """
        self._values = values
    
    def filter(self, filters=None):
        """
        Set any query filters.
        """
        self._filters = filters
    
    def cache(self, toggle=True):
        """
        Enable/disable the cached data flag.
        """
        self._cache = toggle

class APIQuerySet(models.query.QuerySet):
    """
    Query set inheriting from the base Django QuerySet object.
    """
    
    # Timestamp format / timefield keys
    timestamp  = '%Y-%m-%d %H:%M:%S'
    timefields = ['created', 'modified']
    
    # Object extractor
    extract    = APIExtractor()
    
    def __init__(self, *args, **kwargs):
        super(APIQuerySet, self).__init__(*args, **kwargs)
        
    def _key_exists(self, _object, _key):
        """
        Check if an object has a key regardless of value.
        """
        if (_key in _object):
            return True
        return False
        
    def _key_set(self, _object, _key):
        """
        Check if an object contains a specific key, and if the key is not empty.
        """
        if (_key in _object) and _object[_key]:
            return True
        return False
        
    def _parse_metadata(self, _object):
        """
        Parse out any JSON metadata strings.
        """
        
        # Extract metadata values
        if self._key_set(_object, 'meta'):
            try:
                _object['meta'] = json.loads(_object['meta'])
        
            # Could not parse JSON
            except:
                pass
        
    def values_inner(self, *fields):
        """
        Inner processor to return the default results for the values() method.
        """
        
        # Store the initial results
        _values = super(APIQuerySet, self).values(*fields)
        
        # Extract the object information
        for _object in _values:
            
            # Parse any time fields
            for timefield in self.timefields:
                if timefield in _object:
                    _object[timefield] = _object[timefield].strftime(self.timestamp)
            
            # Look for metadata definitions
            self._parse_metadata(_object)
            
        # Return the pre-processed value(s)
        return _values
    
class APIQueryManager(models.Manager):
    """
    Base manager class for API custom querysets.
    """
    def __init__(self, mod, cls, *args, **kwargs):
        super(APIQueryManager, self).__init__()

        # Store the child module / class
        self.mod = mod
        self.cls = cls

    def get_queryset(self, *args, **kwargs):
        """
        Wrapper method for the internal get_queryset() method.
        """
        
        # Get the queryset instance
        queryset = getattr(sys.modules[self.mod], self.cls)
        
        # Return the queryset
        return queryset(model=self.model)