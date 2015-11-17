from importlib import import_module

class ACLObjects(object):
    """
    Wrapper classed used to retrieve ACL object definitions.
    """
    
    @classmethod
    def get_values(cls, obj_type=None):
        """
        Retrieve a list of values for objects by type.
        
        @param obj_type: The type of object to retrieve
        @type  obj_type: str
        """
        
        # Import the required module and create a class instance
        mod = import_module('lense.common.objects.acl.models')
        cls = getattr(mod, 'ACLObjects')
        
        # If an object type is specified
        if obj_type:
            return list(cls.objects.filter(type=obj_type).values())
        
        # Return all object types
        return list(cls.objects.all().values())
    
    @classmethod
    def get(self, obj_type=None):
        """
        Retrieve a collection of objects by type.
        
        @param obj_type: The type of object to retrieve
        @type  obj_type: str
        """
        
        # Import the required module and create a class instance
        mod = import_module('lense.common.objects.acl.models')
        cls = getattr(mod, 'ACLObjects')
        
        # If an object type is specified
        if obj_type:
            return cls.objects.get(type=obj_type)
        
        # Return all object types
        return cls.objects.all()