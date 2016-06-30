from lense import import_class

class ManifestInterface(object):
    """
    Interface class for compiling and executing manifest objects.
    """
    def __init__(self, manifest):
        """
        Initialize the manifest interface, and expose
        methods for compiling and executing the manifest.
        
        :param manifest: The manifest JSON object to compile/execute
        :type  manifest: dict|array
        :rtype: APIResponse
        """
        
        # Setup the manifest backend
        LENSE.MANIFEST.setup(manifest)
        
        # Manifest object manager
        self.manager = import_class('ManifestManager', 'lense.common.manifest.manager')

    def compile(self, dump=False):
        """
        Compile a manifest object.
        """
        return self.manager.compile(dump)
    
    def execute(self):
        """
        Execute a compiled manifest.
        """
        return self.manager.execute()