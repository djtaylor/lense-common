import inspect

class LenseNamespace(object):
    """
    Class object for generating a namespace representation of Lense commons.
    """
    @classmethod
    def inspect_method(cls, name, obj):
        """
        Inspect and return a dictionary representing a class method.
        
        :param name: The method name
        :type  name: str
        :param  obj: The method object
        :type   obj: object
        """
        inspected_method  = inspect.getargspec(obj)
        
        LENSE.LOG.info('INSPECTED_METHOD: {0}, {1}'.format(name, inspected_method))
        
        # Method types
        is_static   = False
        is_class    = False
        is_instance = False
        
        # Ignore self/cls primary arguments
        if (inspected_method.args) and (inspected_method.args[0] in ['self', 'cls']):
            is_class    = True if inspected_method.args[0] == 'cls' else False
            is_instance = True if inspected_method.args[0] == 'self' else False
            inspected_method.args.pop(0)
        else:
            is_static = True
        
        # How many required arguments are there
        num_required_args = 0 if not inspected_method.defaults else len(inspected_method.defaults)
        optional_map      = {} if not inspected_method.defaults else {p: inspected_method.defaults[i] for i,p in enumerate(inspected_method.args[num_required_args:])}
        
        # Construct and return the method representation
        return {
            'name': name,
            'type': 'method',
            'is_static': is_static,
            'is_class': is_class,
            'is_instance': is_instance,
            'args': {
                'required': inspected_method.args[:num_required_args],
                'optional': optional_map
            },
            'use_varargs': True if inspected_method.varargs else False,
            'use_kwargs': True if inspected_method.keywords else False
        }
    
    @classmethod
    def walk_namespace(cls, path, ref):
        """
        Helper method for walking through a namespace level.
        
        :param path: The current namespace path
        :type  path: str
        :param  ref: The referenced namespace object to return
        :type   ref: dict
        """
        for attr in dir(path):
            
            # Ignore self
            if attr == 'NAMESPACE':
                continue
            
            # Ignore private
            if attr.startswith('_'):
                continue
            
            # Attribute object
            attr_obj  = getattr(path, attr)
            attr_type = str(type(attr_obj))
            
            # Object is callable
            if callable(attr_obj):
                
                # Method
                if attr_type == "<type 'instancemethod'>":
                    ref[attr] = cls.inspect_method(attr, attr_obj)
                    
                # Class wrapper
                else:
                    ref[attr] = {
                        'name': attr,
                        'type': 'class',
                        'children': {}
                    }
                    cls.walk_namespace(attr_obj, ref[attr]['children'])
                
            # Object is a variable
            else:
                ref[attr] = {
                    'name': attr,
                    'type': str(type(attr_obj)),
                    'repr': repr(attr_obj)
                }
    
    @classmethod
    def generate(cls):
        """
        Generate a namespace representation.
        """
        ref = {
            'name': 'LENSE',
            'children': {}
        }
        
        # Begin walking through the namespace
        cls.walk_namespace(LENSE, ref['children'])
        
        # Store the generate namespace representation
        LENSE.NAMESPACE = ref