from six import string_types
from json import dumps as jsonDump

# Lense Libraries
from lense.common.exceptions import ManifestError

class _CompiledObject(object):
    """
    Base class for a compiled manifest object.
    """
    def __init__(self, _type, _key, **_attrs):
        self.type  = _type
        self.key   = _key
        
        # Store object attributes
        self.attrs = _attrs
        
        # Calculated value
        self.value = None
        
        # Object state
        self.state = 'compiled'
    
    def __repr__(self):
        return '<{0}#{1}>'.format(self.__class__.__name__, self.key)
    
    def hasattr(self, key):
        """
        Check if the compiled object contains an attribute by key.
        
        :param key: The key to look for
        :type  key: str
        """
        return True if ((key in self.attrs) or (hasattr(self, key))) else False
    
    def getattr(self, key):
        """
        Get a compiled object attribute by key.
        
        :param key: The key to look for
        :type  key: str
        """
        if key in self.attrs:
            return self.attrs[key]
        return getattr(self, key)
    
    def render(self):
        """
        Render the compiled object to a JSON parseable object.
        """
        
        # Append type and key
        self.attrs['type'] = self.type
        self.attrs['key']  = self.key
        
        # Return the rendered object
        return self.attrs
    
    def execute(self):
        """
        Execute the compiled object.
        """
        
        # Variable
        if self.type == 'var':
            
            # Static value (allow empty lists and dictionaries)
            if self.attrs.get('static', False) != False:
                self.value = self.attrs['static']
            
            # Reference another variable
            if self.attrs.get('ref', False):
                self.value = LENSE.MANIFEST.mapReference(self.attrs['ref'])
            
            # Call a method
            if self.attrs.get('call', False):
                exec_method = 'execCommon' if self.attrs['call'].startswith('LENSE') else 'execReference'
            
                # Run the action
                self.value  = getattr(LENSE.MANIFEST, exec_method)(self.attrs['call'], LENSE.MANIFEST.mapArgs(self.attrs.get('args', [])), LENSE.MANIFEST.mapKwargs(self.attrs.get('kwargs', {})))
        
                # Ensure a value
                if self.attrs.get('ensure', False):
                    LENSE.REQUEST.ensure(self.value, **self.attrs['ensure'])
        
            # Fetch a variable
            if self.attrs.get('fetch', False):
                self.value = LENSE.MANIFEST.mapCommon(self.attrs['fetch'])
        
        # Action
        if self.type == 'action':
            exec_method = 'execCommon' if self.attrs['call'].startswith('LENSE') else 'execReference'
            
            # Run the action
            self.value  = getattr(LENSE.MANIFEST, exec_method)(self.attrs['call'], LENSE.MANIFEST.mapArgs(self.attrs.get('args', [])), LENSE.MANIFEST.mapKwargs(self.attrs.get('kwargs', {})))
        
            # Ensure a value
            if self.attrs.get('ensure', False):
                LENSE.REQUEST.ensure(self.value, **self.attrs['ensure'])
        
        # Parameters
        if self.type == '__PARAMS__':
            self.value = self.attrs
        
        # Response
        if self.type == 'response':
            self.value = LENSE.MANIFEST.mapKwargs(self.attrs.get('data', {}))

        # Update the execution state flag
        self.state = 'executed'

    def set(self, key, value):
        """
        Set a new object key/value or update an existing key/value pair.
        """
        
        # Object must be executed to update
        if not self.state == 'executed':
            raise ManifestError('Compiled object {0} must be executed before setting/updating values'.format(repr(self)))
            
        # Set the new value
        self.value[key] = value

class CompiledVariable(_CompiledObject):
    """
    Class object for storing a compiled variable.
    """
    def __init__(self, key, kwargs):
        super(CompiledVariable, self).__init__('var', key, **kwargs)

class CompiledAction(_CompiledObject):
    """
    Class object for storing a method action.
    """
    def __init__(self, key, mapping):
        super(CompiledAction, self).__init__('action', key, **mapping)

class CompiledResponse(_CompiledObject):
    """
    Class object for storing a compiled response.
    """
    def __init__(self, kwargs):
        super(CompiledResponse, self).__init__('response', 'response', **kwargs)

class CompiledParameters(_CompiledObject):
    """
    Class object for storing compiled request parameters.
    """
    def __init__(self, params):
        super(CompiledParameters, self).__init__('__PARAMS__', '__PARAMS__', **params)
        
        # Request data container
        self.data = None
        
    def validate(self):
        """
        Validate compiled request parameters.
        """
        
        # Reject unsupported parameters
        for k,v in self.data.value.iteritems():
            if not k in self.value:
                raise ManifestError('Supplied unsupported attribute: {0}'.format(k))
        
        # Validate parameters against request data
        for p,a in self.value.iteritems():
            
            # Parameter required but not present
            if (a[0] == True) and not (p in self.data.value):
                
                # No default value found
                if not a[1]: 
                    raise ManifestError('Missing required parameter: {0}'.format(p))
                else:
                    
                    # Default value can be a string or dictionary mapping
                    if not isinstance(a[1], (string_types, dict)):
                        raise ManifestError('Default value mapping for {0} must be a string or dictionary type'.format(p))
        
                    # Dictionary mapping
                    if isinstance(a[1]) and not ('call' in a[1]):
                        raise ManifestError('Missing required parameter "call" in default value mapping for {0}'.format(p))
        
    def process(self):
        """
        Process compiled request parameters.
        """
        for p,a in self.value.iteritems():
            
            # Assign any default values
            if not (p in self.data.value) and (a[1]):
                
                # String mapping
                if isinstance(a[1], string_types):
                    
                    # Commons mapping
                    if a[1].startswith('LENSE'):
                        mapped = LENSE.MANIFEST.mapCommon(a[1])
                        
                        # Callable method
                        if callable(mapped):
                            self.data.set(p, mapped())
                            
                        # Variable
                        else:
                            self.data.set(p, mapped)
                        
                    # Static value
                    else:
                        self.data.set(p, a[1])
                    
                # Dictionary mapping
                if isinstance(a[1], dict):
                    self.data.set(p, LENSE.MANIFEST.execCommon(a[1]['call'], args=a[1].get('args', []), kwargs=a[1].get('kwargs', {})))
        
    def execute(self):
        """
        Execute and validate request parameters.
        """
        super(CompiledParameters, self).execute()

        # Get request data
        self.data = LENSE.MANIFEST.COMPILED.get('__DATA__')
                
        # Validate and process request parameters
        self.validate()
        self.process()

class CompiledManifest(object):
    """
    Class object representing a compiled manifest object.
    """
    def __init__(self):
        self.objects  = []
        self.uuid     = LENSE.uuid4()
        
    def __repr__(self):
        return '<{0}#{1}>'.format(self.__class__.__name__, self.uuid)
        
    def haskey(self, key):
        """
        Check if the compiled manifest has an object with a specified reference key.
        
        :param key: The reference key to check for
        :type  key: str
        :rtype: bool
        """
        for obj in self.objects:
            if obj.key == key:
                return True
        return False
        
    def getkey(self, key):
        """
        Get a compiled object by reference key.
        
        :param key: The reference key to check for
        :type  key: str
        :rtype: CompiledObject
        """
        for obj in self.objects:
            if obj.key == key:
                return obj
        raise ManifestError('Unable to locate reference key "{0}" in {1}'.format(key, repr(self)))
    
    def dump(self):
        """
        Dump all compiled objects to their representations.
        """
        return jsonDump([x.render() for x in self.objects])
        
    def append(self, obj, position=None):
        """
        Append a compiled manifest object to the objects container.
        
        :param obj: The manifest object to append
        :type  obj: object
        """
        
        # Cannot duplicated reference keys
        if self.haskey(obj.key):
            raise ManifestError('Cannot have a duplicate reference key "{0}" in {1}'.format(obj.key, repr(self)))
        
        # Put at a specific position
        if isinstance(position, int):
            self.objects.insert(position,obj)
            
        # Store the compiled object
        else:
            self.objects.append(obj)
                
    def appendResponse(self, params):
        """
        Helper method for storing a compiled response.
        
        :param params: The compiled response parameters
        :type  params: dict
        """
        self.append(CompiledResponse(params))
        
    def define_action(self, key, mapping):
        """
        Define a new action.
        
        :param     key: The action reference key
        :type      key: str
        :param mapping: The method mapping attributes
        :type  mapping: dict
        """
        self.append(CompiledAction(key, mapping))
        
    def define_params(self, params):
        """
        Define parameter customizations.
        """
        self.append(CompiledParameters(params))
        
    def define_var(self, key, value, ref=None, mapping=None, commons=None, position=None):
        """
        Define a new variable.
        
        :param     key: The variable key
        :type      key: str
        :param   value: A static variable value
        :type    value: mixed
        :param     ref: The referenced variable
        :type      ref: str
        :param mapping: A method mapping
        :type  mapping: dict
        :param commons: A Lense commons mapping
        :type  commons: str
        """
        static = all(x is None for x in [ref, mapping, commons])
        
        # Static value
        if static:
            self.append(CompiledVariable(key, {
                'static': value
            }), position=position)
            
        # Reference value
        if ref:
            self.append(CompiledVariable(key, {
                'ref': value
            }), position=position)
            
        # Method mapping
        if mapping:
            self.append(CompiledVariable(key, {
                'call': value['call'],
                'kwargs': value.get('kwargs', {}),
                'args': value.get('args', []),
                'ensure': value.get('ensure', False)
            }), position=position)
        
        # Commons mapping
        if commons:
            self.append(CompiledVariable(key, {
                'fetch': value
            }), position=position)
        
    def delete(self, key):
        """
        Delete a compiled object by its reference key.
        
        :param key: The object reference key
        :type  key: str
        """
        if not self.haskey(key):
            raise ManifestError('Cannot delete object reference key "{0}" in {1}, no such key'.format(key, repr(self)))
        
        # Delete the compiled object
        index = None
        for i,o in enumerate(self.objects):
            if o['key'] == key:
                index = i
        
        # Delete the object
        del self.objects[index]
        
    def get(self, key, attr=None, default=None):
        """
        Get a compiled object by its reference key, optionally extracting a sub-attribute.
        
        :param     key: The object reference key
        :type      key: str
        :param    attr: The sub-attribute key to extract
        :type     attr: str
        :param default: An optional default value to return
        :type  default: mixed
        :rtype: mixed
        """
        
        # Make sure the compiled object has the reference key
        if not self.haskey(key):
            if default:
                return default
            raise ManifestError('Cannot find object reference key "{0}" in {1}'.format(key, repr(self)))
        
        # Get the referenced object
        refobj = self.getkey(key)
        
        # If extracting an attribute
        if attr:
            if not refobj.hasattr(attr):
                raise ManifestError('Cannot extract attribute "{0}" from {1}, no such key'.format(attr, repr(self)))
            
            # Return the extracted attribute
            return refobj.getattr(attr)
        
        # Return the entire object
        return refobj
    
    def check_duplicate(self, key):
        """
        Raise a ManifestError if duplicate key found.
        
        :param key: The key check duplicates for
        :type  key: str
        """
        if self.haskey(key):
            raise ManifestError('Duplicate key #{0} detected, keys must be unique'.format(key))