import re
import json
from inspect import isclass
from six import string_types, integer_types

# Lense Libraries
from lense.common.exceptions import ManifestError
from lense.engine.api.handlers import RequestOK

class ManifestManager(object):
    """
    Class object for managing manifest compilation and execution.
    """
    def log(self, msg, level='info', method=None):
        """
        Wrapper method for logging with a prefix.
        
        :param    msg: The message to log
        :type     msg: str
        :param  level: The desired log level
        :type   level: str
        :param method: Optionally append the method to log prefix
        :type  method: str
        """
        logger = getattr(LENSE.LOG, level, 'info')
        logger('<{0}{1}> {2}'.format(
            self.__class__.__name__, 
            '' if not method else '.{0}'.format(method),
            msg
        ))
    
    def _compileResponse(self, data={}):
        """
        Compile a response object.
        
        :param data: Any response data
        :type  data: dict
        """
        
        # Log the response compile process
        self.log('Compiling response', level='info', method='_compileResponse')

        # Store the compiled response
        LENSE.MANIFEST.COMPILED.appendResponse({
            'data': data
        })
        
    def _compileAction(self, key, mapping):
        """
        Compile a manifest action.
        
        :param     key: The key to reference the action
        :type      key: str
        :param mapping: The action mapping
        :type  mapping: dict
        """
        key = re.compile(r'^do#(.*$)').sub(r'\g<1>', key)
        
        # Cannot duplicate keys
        LENSE.MANIFEST.COMPILED.check_duplicate(key)
        
        # Call attribute required
        if not 'call' in mapping:
            raise ManifestError('Must define a "call" attribute key for an action mapping!')
        
        # Compiling action
        self.log('Compiling action #{0} -> {1}'.format(key, mapping), level='info', method='_compileAction')
        
        # Store the action
        LENSE.MANIFEST.COMPILED.define_action(key, mapping)
        
    def _compileVariable(self, key, value):
        """
        Compile a variable definition.
        
        :param   key: The variable key mapping
        :type    key: str
        :param value: The variable value mapping
        :type  value: str|dict
        """
        key = re.compile(r'^var#(.*$)').sub(r'\g<1>', key)
    
        # Cannot duplicate keys
        LENSE.MANIFEST.COMPILED.check_duplicate(key)
        
        # Value must be a valid type
        if not isinstance(value, (string_types, integer_types, dict, list)):
            raise ManifestError('Variable #{0} value must be a string or dictionary, found type({1}) instead'.format(key, type(value)))
    
        # Compiling variable
        self.log('Compiling variable #{0} = {1}'.format(key, repr(value)), level='info', method='_compileVariable')
        
        # Method mapping
        if isinstance(value, dict) and ('call' in value):
            LENSE.MANIFEST.COMPILED.define_var(key, value, mapping=True)
            
        # Dictionary / list value
        elif isinstance(value, (dict, list)):
            LENSE.MANIFEST.COMPILED.define_var(key, value)
            
        # Reference
        elif value.startswith('#'):
            LENSE.MANIFEST.COMPILED.define_var(key, value[1:], ref=True)
        
        # Commons
        elif value.startswith('LENSE'):
            LENSE.MANIFEST.COMPILED.define_var(key, value, commons=True)
            
        # Static
        else:
            LENSE.MANIFEST.COMPILED.define_var(key, value)
    
    def _compileParameters(self, params):
        """
        Compile request parameter customization if provided.
        """
        
        # Parameters must be a dictionary
        if not isinstance(params, dict):
            raise ManifestError('Request parameters must be a dictionary, not type({0})'.format(type(data)))
    
        # Each parameter must be a key / list pair
        for param, attrs in params.iteritems():
            if not isinstance(attrs, list) or not (len(attrs) == 2):
                raise ManifestError('Parameter definition for {0} must be a 2-element list: i.e. [required (true|false), default_value (static|mapping)]'.format(param))
    
            # First attribute must be a boolean
            if not isinstance(attrs[0], bool):
                raise ManifestError('First list attribute for parameter {0} must be a boolean value'.format(param))
    
            # No default value
            if attrs[1] == None:
                continue
    
            # Second attribute validation
            if not isinstance(attrs[1], (string_types, dict, integer_types, bool)):
                raise ManifestError('Second list attribute for parameter {0} must be a string/integer/bool/dictionary, or null for no default'.format(param))
    
        # Store parameter customization as a variable
        LENSE.MANIFEST.COMPILED.define_params(params)
    
    def _compileData(self, data):
        """
        Compile request data overrides if present.
        """
        
        # Request data must be a dictionary
        if not isinstance(data, dict):
            raise ManifestError('Request data overrides must be a dictionary, not type({0})'.format(type(data)))
    
        # Compiling request data
        self.log('Compiling request data: __DATA__ = {0}'.format(data))
        
        # Store request data overrides as a variable reference
        LENSE.MANIFEST.COMPILED.define_var('__DATA__', data, position=0)
    
    def _toJSON(self, obj):
        """
        Convert a response object to a JSON friendly format.
        """
        
        # String object
        if isinstance(obj, string_types):
            return obj
        
        # Integer object
        elif isinstance(obj, integer_types):
            return obj
        
        # List object
        elif isinstance(obj, list):
            for i,o in enumerate(obj):
                obj[i] = self._toJSON(o)
                
        # Dictionary object
        elif isinstance(obj, dict):
            for k,v in obj.iteritems():
                obj[k] = self._toJSON(v)
          
        # Class object
        else:
            
            # Try to dump a Lense object
            try:
                return LENSE.OBJECTS.dump(obj)
            
            # Object does not support dump method
            except Exception as e:
                self.log('Failed to dump object: {0}: {1}'.format(repr(obj), str(e)), level='debug', method='_toJSON')
            
        # Log the processed response object
        self.log('Processing response object: type={0}, content={1}'.format(type(obj), repr(obj)))
            
        # Return the response object
        return obj
            
    def compile(self, dump):
        """
        Compile the JSON manifest.
        
        :param dump: Dump the representations of compiled objects
        :type  dump: bool
        :rtype: dict
        """
        
        try:
            LENSE.NAMESPACE.generate()
            LENSE.LOG.info('GENERATED_NAMESPACE: {0}'.format(json.dumps(LENSE.NAMESPACE)))
        except Exception as e:
            LENSE.LOG.exception('Failed to generate namespace: {0}'.format(str(e)))
        
        # Must be a list of definitions
        if not isinstance(LENSE.MANIFEST.json, list):
            raise ManifestError('Parent block must be a list, found type({0}) instead'.format(type(LENSE.MANIFEST.json)))
        
        # Default request data
        request_data = LENSE.REQUEST.data
        
        # Compiled each definition
        for i,d in enumerate(LENSE.MANIFEST.json):
            if len(d) != 1:
                raise ManifestError('Each block definition may contain only 1 key/value pair!')
            for k,v in d.iteritems():
                
                # Request data override must be the first definition
                if k == '__DATA__' and not (i == 0):
                    raise ManifestError('Request data override must be the first definition!')
                
                # Request data overrides
                if k == '__DATA__':
                    self.log('Overridding request data: {0}'.format(v), level='info', method='compile')
                    request_data = v
                
                # Parameter customization
                elif k == '__PARAMS__':
                    self._compileParameters(v)
                
                # Variable definition
                elif re.match(r'^var#[a-zA-Z0-9_]*$', k):
                    self._compileVariable(k,v)
                
                # Action definition
                elif re.match(r'^do#[a-zA-Z0-9_]*$', k):
                    self._compileAction(k,v)
                
                # Response definition
                elif k == 'response':
                    self._compileResponse(v)
        
                # Invalid definition key
                else:
                    raise ManifestError('Invalid definition key: {0}'.format(k))
            
        # Store request data
        self._compileData(request_data)
            
        # Return the compiled manifest
        return LENSE.MANIFEST.COMPILED.dump() if dump else LENSE.MANIFEST.COMPILED.objects
    
    def execute(self):
        """
        Execute the compiled manifest.
        """
        
        # Compile the manifest
        self.compile(False)
        
        # Execute the compiled object
        for obj in LENSE.MANIFEST.COMPILED.objects:
            obj.execute()
            self.log('Executed compiled object {0}, value={1}, type={2}'.format(repr(obj), repr(obj.value), type(obj.value)), level='debug', method='execute')
        
        # If a response is defined
        if LENSE.MANIFEST.COMPILED.haskey('response'):
            return self._toJSON(LENSE.MANIFEST.COMPILED.get('response').value)