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

    def execCommon(self, path, args=[], kwargs={}):
        """
        Execute a Lense commons mapping.
        """
        return self.mapCommon(path)(*args, **kwargs)

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

    def mapArgs(self, args):
        """
        Map required arguments for compiled variables.
        """
        if isinstance(args, list):
            for k,v in enumerate(args):
                if isinstance(v, bool) or v is None:
                    args[k] = v
                elif isinstance(v, integer_types):
                    args[k] = v
                elif isinstance(v, dict):
                    if 'call' in v:
                        args[k] = self.execCommon(v['call'], v.get('args', []), v.get('kwargs', {}))
                    else:
                        args[k] = self.mapKwargs(v)
                elif isinstance(v, list):
                    args[k] = self.mapArgs(v)
                else:
                    if v.startswith('#'):
                        args[k] = self.mapReference(v[1:])
                    if v.startswith('LENSE'):
                        args[k] = self.mapCommon(v)
            return args
        elif args.startswith('#'):
            return self.mapReference(args[1:])
        elif args.startswith('*'):
            return self.mapCommon(args[1:])

    def mapKwargs(self, kwargs):
        """
        Map keyword arguments for compiled variables.
        """
        if isinstance(kwargs, dict):
            for k,v in kwargs.iteritems():
                if isinstance(v, bool) or v is None:
                    kwargs[k] = v
                elif isinstance(v, integer_types):
                    kwargs[k] = v
                elif isinstance(v, dict):
                    if 'call' in v:
                        kwargs[k] = self.execCommon(v['call'], v.get('args', []), v.get('kwargs', {}))
                    else:
                        kwargs[k] = self.mapKwargs(v)
                elif isinstance(v, list):
                    kwargs[k] = self.mapArgs(v)    
                else:
                    if v.startswith('#'):
                        kwargs[k] = self.mapReference(v[1:])
                    if v.startswith('LENSE'):
                        kwargs[k] = self.mapCommon(v)
            return kwargs
        elif kwargs.startswith('#'):
            return self.mapReference(kwargs[1:])
        elif kwargs.startswith('**'):
            return self.mapCommon(kwargs[2:])
        
    @classmethod
    def setup(cls, manifest):
        """
        Class method for setting up the manifest backend.
        """
        LENSE.MANIFEST = cls(manifest)