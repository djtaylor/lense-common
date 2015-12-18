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

    def filter(self, **kwargs):
        """
        Apply filters to the current object query.
        """
        return self.model.objects.filter(**kwargs)

    def exists(self, **kwargs):
        """
        Check if an object exists.
        """
        return self.model.objects.filter(**kwargs).count()
    
    def update(self, **kwargs):
        """
        Update an existing object.
        """
        obj  = self.get(**kwargs)
        uuid = kwargs.get('uuid', None)
        
        # Object doesn't exist, cannot updated
        if not obj:
            LENSE.LOG.debug('Cannot update <{0}:{1}>, object does not exist'.format(self.cls, uuid))
            return False
        
        # Update the object
        try:
            obj.update(**kwargs)
            return True
        
        # Failed to update object
        except Exception as e:
            LENSE.LOG.exception('Failed to update <{0}:{1}>: {1}'.format(self.cls, str(e)))
    
    def create(self, **params):
        """
        Create a new object
        """
        try:
            
            # Create/save the object
            obj = self.model(**params)
            obj.save()
            
            # Return the new object
            return obj
        
        # Failed to create the object
        except Exception as e:
            LENSE.LOG.exception('Failed to create {0}: {1}'.format(self.cls, str(e)))
            return False
    
    def delete(self, **kwargs):
        """
        Delete an object definition.
        """
        obj  = self.get(**kwargs)
        uuid = kwargs.get('uuid', None)
        
        # Object doesn't exist, cannot delete
        if not obj:
            LENSE.LOG.debug('Cannot delete <{0}:{1}>, object does not exist'.format(self.cls, uuid))
            return False
        
        # Delete the object
        try:
            obj.delete()
            return True

        # Failed to delete the object
        except Exception as e:
            LENSE.LOG.exception('Failed to delete <{0}:{1}>: {2}'.format(self.cls, uuid, str(e)))
            return False
    
    def get(self, **kwargs):
        """
        Retrieve an object definition.
        """
        
        # Retrieving all
        if not kwargs:
            return self.model.objects.all()
    
        # Retrieving by parameters
        return self.model.objects.get(**kwargs)