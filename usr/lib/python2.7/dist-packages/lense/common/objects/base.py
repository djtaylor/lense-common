from uuid import UUID
from lense import import_class
from lense.common.exceptions import RequestError

class LenseBaseObject(object):
    """
    Common class shared by object interfaces.
    """
    def __init__(self, mod, cls):
        """
        :param mod: The object model module
        :type  mod: str
        :param cls: The object model class
        :type  cls: str
        """
        self.module = mod
        self.cls    = cls
        
        # Get the object model
        self.model  = import_class(cls, mod, init=False)

    def map_id(self, idstr, key):
        """
        Map an identity string to a keyword (UUID or other)
        """
        try:
            UUID(group, version=4)
            return {'uuid': group}
        except ValueError:
            return {'name': group}

    def exists(self, **kwargs):
        """
        Check if an object exists.
        """
        return self.model.objects.filter(**kwargs).count()
    
    def update(self, uuid, **kwargs):
        """
        Update an existing object.
        
        :param   uuid: Retrieve an object to update via UUID
        :type    uuid: str
        """
        obj = self.get(uuid=uuid)
        
        # Object doesn't exist, cannot updated
        if not obj:
            return False
        
        # Update the object
        obj.update(**kwargs)
        return True
    
    def create(self, **params):
        """
        Create a new object
        """
        try:
            obj = self.model(**params)
            obj.save()
            return True
        except Exception as e:
            LENSE.LOG.exception('Failed to save {0}: {1}'.format(self.cls, str(e)))
            return False
    
    def delete(self, **kwargs):
        """
        Delete an object definition.
        """
        obj = self.get(**kwargs)
        
        # Object doesn't exist, cannot delete
        if not obj:
            return False
        
        # Delete the object
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