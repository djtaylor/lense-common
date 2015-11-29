from lense import import_class

class LenseAPIConstructor(object):
    """
    Helper class for constructing API classes.
    """
    @staticmethod
    def BASE(self, *args, **kwargs):
        """
        Wrapper method for returning an instance of APIBase.
        """
        return import_class('APIBase', 'lense.engine.api.base', args=args, kwargs=kwargs).construct()
    
    @staticmethod
    def BARE(self, *args, **kwargs):
        """
        Wrapper method for returning an instance of APIBare.
        """
        return import_class('APIBare', 'lense.engine.api.bare', args=args, kwargs=kwargs)