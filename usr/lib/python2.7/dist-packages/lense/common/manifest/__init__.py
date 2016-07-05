from six import string_types, integer_types

# Lense Libraries
from lense import import_class
from lense.common.exceptions import ManifestError

class LenseManifest(object):
    """
    Commons interface class for compiling and executing manifests.
    """
    def __init__(self, manifest):
        self.json     = manifest
        self.COMPILED = import_class('CompiledManifest', 'lense.common.manifest.compiled')
        self.MANAGER  = import_class('ManifestManager', 'lense.common.manifest.manager')
        
    def mapCommon(self, path):
        """
        Map to a commons object.
        """
        paths  = path.split('.')
        mapped = LENSE
        for p in paths:
            
            # Root namespace
            if p == 'LENSE':
                continue
            
            # Make sure mapping key exists
            if not hasattr(mapped, p):
                raise ManifestError('Invalid mapping path: {0}'.format(path))
            
            # Store the next mapping
            mapped = getattr(mapped, p)
            
        # Return the mapped path
        return mapped

    def mapReference(self, key):
        """
        Map a variable reference.
        
        :param key: The reference key
        :type  key: str
        :rtype: mixed
        """
        objkeys = None
        
        # Request data reference
        if key == '__DATA__':
            if not self.COMPILED.haskey(key):
                return LENSE.REQUEST.data
            return self.COMPILED.get(key).value
        
        # Are we mapping to object attributes
        if '.' in key:
            objkeys = key.split('.')
            key     = objkeys[0]
            objkeys.pop(0)

        # Reference key does not exist
        if not LENSE.MANIFEST.COMPILED.haskey(key):
            raise ManifestError('Variable contains an undefined key reference: {0}'.format(key))

        # Object keys
        if objkeys:
            top    = self.COMPILED.get(key).value
            refval = LENSE.OBJECTS.walkattr(top, objkeys)
            
        # Top level reference
        else:
            refval = self.COMPILED.get(key).value

        # Return the value
        return refval

    def execCommon(self, path, args=[], kwargs={}):
        """
        Execute a Lense commons mapping.
        """
        return self.mapCommon(path)(*args, **kwargs)

    def execReference(self, path, args=[], kwargs={}):
        """
        Execute an internal reference mapping.
        """
        return self.mapReference(path[1:])(*args, **kwargs)

    def mapInner(self, walk):
        """
        Abstract method for mapping both args and kwargs objects.
        """
        
        # Mapping is iterable
        if isinstance(walk, (list, dict)):
            for k,v in (enumerate(walk) if isinstance(walk, list) else walk.iteritems()):
                
                # Boolean value
                if isinstance(v, bool) or v is None:
                    walk[k] = v
                    
                # Number value
                elif isinstance(v, integer_types):
                    walk[k] = v
                    
                # Nested keyword arguments
                elif isinstance(v, dict):
                    
                    # Method mapping
                    if 'call' in v:
                        exec_method = self.execCommon if v['call'].startswith('LENSE') else self.execReference
                        exec_method(v['call'], v.get('args', []), v.get('kwargs', {}))
                    else:
                        walk[k] = self.mapInner(v)
                        
                # Nested arguments
                elif isinstance(v, list):
                    walk[k] = self.mapInner(v)
                
                # Reference
                else:
                    
                    # Internal reference
                    if v.startswith('#'):
                        walk[k] = self.mapReference(v[1:])
                        
                    # Commons reference
                    if v.startswith('LENSE'):
                        walk[k] = self.mapCommon(v)
            
            # Return mapped arguments
            return walk
        
        # Map reference
        elif walk.startswith('#'):
            return self.mapReference(walk[1:])
        
        # Map arguments
        elif walk.startswith('*'):
            return self.mapCommon(walk[1:])
        
        # Map keyword arguments
        elif walk.startswith('**'):
            return self.mapCommon(walk[2:])
        
        # Unsupported mapping
        else:
            raise ManifestError('Cannot parse arguments: {0}'.format(str(walk)))

    def mapArgs(self, args):
        """
        Map required arguments for compiled variables.
        """
        return self.mapInner(args)

    def mapKwargs(self, kwargs):
        """
        Map keyword arguments for compiled variables.
        """
        return self.mapInner(kwargs)
        
    @classmethod
    def setup(cls, manifest):
        """
        Class method for setting up the manifest backend.
        """
        LENSE.MANIFEST = cls(manifest)
    
    @classmethod
    def compile(cls, dump):
        """
        Wrapper method for calling the manifest manager compile method.
        """
        return self.MANAGER.compile(dump)
    
    @classmethod
    def execute(cls):
        """
        Wrapper method for calling the manifest manager execute method.
        """
        return self.MANAGER.execute()