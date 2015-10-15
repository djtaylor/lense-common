import re
import json
from types import InstanceType, ClassType
from collections import namedtuple

class Collection(object):
    """
    Class used to generate a named tuple collection from any number
    of dictionaries. Returns an immutable collection oject.
    
    Initialize a collection::
    
        # Import the collection class
        from lense.common.collection import Collection
        
        # Create an empty collection
        c1 = Collection()
        
        # Create a collection with initial data
        c2 = Collection({'one': 'value1', 'two': 'value2'})
    """
    def __init__(self, init_data=None):
        """
        Initialize a new collection object.
        
        :param init_data: An optional dictionary used to initialize the collection
        :type init_data: dict
        """
        self.class_name = self.__class__.__name__
        if init_data:
            if isinstance(init_data, dict):
                
                # Check if creating a collection from a Django QueryDict
                if re.match(r'^<QueryDict.*$', str(init_data)):
                    self.collection = self._convert_query_dict(init_data)
                else:
                    self.collection = init_data
            else:
                self.collection = {}
        else:
            self.collection = {}

    def _convert_query_dict(self, query_dict):
        """
        Helper method used to convert a Django QueryDict to a standard
        Python dictionary.
        
        :param query_dict: The Django QueryDict object to convert
        :type query_dict: QueryDict
        """
        raw_converted = dict(query_dict.iterlists())
        converted = {}
        for key, value in raw_converted.iteritems():
            converted[key] = value[0]
        return converted

    def merge_dict(self, a, b, path=None):
        """
        Merge two dictionaries together. Do not overwrite duplicate keys.
        
        Merging dictionaries::
        
            # Import the collection class
            from lense.common.collection import Collection
        
            # Create a collection object
            collection = Collection()
        
            # Base dictionaries
            d1 = {'one': 'value1', 'two': 'value2', 'three': {'arg1': 'somevalue'}}
            d2 = {'three': {'arg2': 'value2', 'arg3': 'value3'}}
            
            # Merged dictionary
            dm = collection.merge_dict(d1, d2)
            
        The new dictionary::
        
            {
                'one': 'value1',
                'two': 'value2',
                'three': {
                    'arg1': 'somevalue',
                    'arg2': 'value2',
                    'arg3': 'value3'
                }
            }
        
        :param a: The first dictionary
        :type a: dict
        :param b: The second dictionary
        :type b: dict
        :param path: Not really sure what this does, using re-purposed code here
        :type path: list
        """
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    self.merge_dict(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass
                else:
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a

    def map(self, map_dict={}):
        """
        Map a dictionary to an existing collection object.
        
        Mapping a new dictionary object::
        
            # Import the collection class
            from lense.common.collection import Collection
        
            # Create a collection object
            collection = Collection({'data': {'key1': 'value1'}})
            
            # Map a new dictionary
            collection.map({'data': {'key2': 'value2'}})
        
        The new dictionary::
        
            {
                'data': {
                    'key1': 'value1',
                    'key2': 'value2'
                }
            }
        
        :param map_dict: The dictionary object to map
        :type map_dict: dict
        """
        if not map_dict: 
            return None
        else:
           
            # Check if mapping a Django QueryDict
            if re.match(r'^<QueryDict.*$', str(map_dict)):
                self.collection = self.merge_dict(self._convert_query_dict(map_dict), self.collection)
            else:
                self.collection = self.merge_dict(map_dict, self.collection)
       
    def isclass(self, obj, cls):
        """
        Helper method to test if an object is either a new or old style class.
        
        :param obj: The object to test
        :type obj: *
        :rtype: boolean
        """
        
        # Test for an old style class
        if (type(obj) is InstanceType):
            return True
        
        # Test for a class object
        if (re.match(r'^<lense\..[^>]*>$', str(obj))):
            return True
        
        # Test for a new style class
        if ((hasattr(obj, '__class__')) and (re.match(r'^<class \'lense\..*\.%s\'>$' % cls, repr(obj.__class__)))):
            return True
        return False
       
    def get(self):
        """
        Retrieve the constructed collection objects. Converts the internal
        dictionary collection to a named tuple.
        
        Constructing a collection::
        
            # Import the collection class
            from lense.common.collection import Collection
        
            # Create a collection object
            collection = Collection()
            
            # Map collection data
            collection.map({'key1': {'subkey1': 'value1', 'subkey2': 'value2'}})
        
            # Get the named tuple
            newcol = collection.get()
        
        Accessing collection data::
        
            # Get subkey2
            print newcol.key1.subkey2
        
        :rtype: namedtuple
        """
        def obj_mapper(d):
            """
            Map a dictionary to a named tuple object based on dictionary keys
            
            :param d: The dictionary to map
            :type d: dict
            :rtype: namedtuple
            """
            return namedtuple(self.class_name, d.keys())(*d.values())
        
        # Check if creating a collection of classes
        class_collection = False
        for key, obj in self.collection.iteritems():
            if self.isclass(self.collection[key], key):
                class_collection = True
                break
        
        # Map the data to an object and return
        if class_collection:
            return namedtuple(self.class_name, self.collection.keys())(*self.collection.values())
        else:
            data = json.dumps(self.collection)
            return json.loads(data, object_hook=obj_mapper)