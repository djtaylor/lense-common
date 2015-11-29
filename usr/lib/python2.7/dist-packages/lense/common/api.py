class LenseAPIConstructor(object):
    """
    Helper class for constructing API classes.
    """
    @staticmethod
    def BASE(self, *args, **kwargs):
        from lense.engine.api.base import APIBase
    
        # Construct and return APIBase
        return APIBase(*args, **kwargs).construct()
    
    @staticmethod
    def BARE(self, *args, **kwargs):
        from lense.engine.api.bare import APIBare

        # Construct and return APIBare
        return APIBare(*args, **kwargs)