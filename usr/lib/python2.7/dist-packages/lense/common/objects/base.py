from lense import import_class

class LenseBaseObject(object):
    """
    Common class shared by object interfaces.
    """
    def __init__(self, mod, cls):
        self.module = mod
        self.cls    = cls
        
        # Get the object model
        self.model  = import_class(cls, mod, init=False)

    def exists(self, **kwargs):
        """
        Check if an object exists.
        """
        return self.model.objects.filter(**kwargs).count()
    
    def update(self, uuid, **kwargs):
        """
        Update an existing object.
        """
        obj = self.get(uuid=uuid)
        if not obj:
            return False
        obj.update(**kwargs)
        return True
    
    def create(self, **params):
        """
        Create a new object
        """
        obj = self.model(**params)
        obj.save()
        print 'OBJ: {0}'.format(repr(obj))
        return obj
    
    def delete(self, **kwargs):
        """
        Delete an object definition.
        """
        obj = self.get(**kwargs)
        if not obj:
            return False
        obj.delete()
        return True
    
    def get(self, **kwargs):
        """
        Retrieve an object definition.
        """
        
        # Retrieving all
        if not kwargs:
            return self.model.objects.all()
    
        # Retrieving by parameters
        return self.model.ojects.get(**kwargs)