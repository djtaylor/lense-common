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

        LENSE.LOG.info('@MANIFEST: compiling = {0}'.format(manifest))

        # Setup the manifest backend
        LENSE.MANIFEST.setup(manifest)

    def compile(self, dump=False):
        """
        Compile a manifest object.
        """
        return LENSE.MANIFEST.MANAGER.compile(dump)

    def execute(self):
        """
        Execute a compiled manifest.
        """
        return LENSE.MANIFEST.MANAGER.execute()
