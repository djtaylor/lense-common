from uuid import UUID

# Django Libraries
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# Lense Libraries
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
        
        # Get the object model / unique ID field
        self.model  = import_class(cls, mod, init=False)
        self.uidf   = self.model.UID_FIELD

        # Debug log prefix
        self.logpre = 'OBJECTS:{0}'.format(self.cls)

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
        logger('<{0}{1}> {2}'.format(self.logpre, '' if not method else '.{0}'.format(method), msg))

    def is_email(self, emailstr):
        """
        Check if a user string is an email.
        
        :param emailstr: The email string to check
        :type  emailstr: str
        :rtype: str|False
        """
        try:
            validate_email(emailstr)
            return emailstr
        except ValidationError as e:
            return False

    def is_uuid(self, idstr):
        """
        Check if a user string is a UUID.
        
        :param idstr: The user string to check
        :type  idstr: str
        :rtype: str|False
        """
        try:
            UUID(idstr, version=4)
            return idstr
        except:
            return False

    def exists(self, **kwargs):
        """
        Check if an object exists.
        """
        count = self.model.objects.filter(**kwargs).count()
        self.log('Found {0} object(s) -> filter={1}'.format(str(count), str(kwargs)), level='debug', method='exists')
        return count
    
    def update(self, **kwargs):
        """
        Update an existing object.
        """
        obj = self.get(**kwargs)
        uid = '{0}={1}'.format(self.uidf, getattr(kwargs, self.uidf))
        
        # Object doesn't exist, cannot updated
        if not obj:
            self.log('Cannot update object -> {0}: Does not exist'.format(uid), level='debug', method='update')
            return False
        
        # Update the object
        try:
            obj.update(**kwargs)
            self.log('Updated object -> {0}'.format(uid), level='debug', method='update')
            return True
        
        # Failed to update object
        except Exception as e:
            self.log('Failed to update object -> {0}: {1}'.format(uid, str(e)), level='exception', method='update')
            return False
    
    def create(self, **kwargs):
        """
        Create a new object
        """
        try:
            
            # Create/save the object
            obj = self.model(**kwargs)
            obj.save()
            uid = '{0}={1}'.format(self.uidf, getattr(obj, self.uidf))
            self.log('Created object -> {0}'.format(uid), level='debug', method='create')
            
            # Return the new object
            return obj
        
        # Failed to create the object
        except Exception as e:
            self.log('Failed to create object -> {0}'.format(str(e)), level='exception', method='create')
            return False
    
    def delete(self, **kwargs):
        """
        Delete an object definition.
        """
        obj = self.get(**kwargs)
        uid = '{0}={1}'.format(self.uidf, kwargs.get(self.uidf, None))
        
        # Object doesn't exist, cannot delete
        if not obj:
            self.log('Cannot delete object -> {0}: Does not exist'.format(uid), level='debug', method='delete')
            return False
        
        # Delete the object
        try:
            obj.delete()
            self.log('Deleted object -> {0}'.format(uid), level='debug', method='delete')
            return True

        # Failed to delete the object
        except Exception as e:
            self.log('Failed to delete object -> {0}: {1}'.format(uid, str(e)), level='exception', method='delete')
            return False
    
    def filter(self, **kwargs):
        """
        Retrieve multiple objects in a list format.
        """
        objects = self.model.objects.filter(**kwargs)
        
        # No objects found
        if not objects.count():
            self.log('No objects found -> filter={0}'.format(str(kwargs)), level='debug', method='filter')
            return []
        
        # Return objects in a list
        self.log('Retrieved objects -> count={0}, filter={1}'.format(objects.count(), str(kwargs)), level='debug', method='filter')
        return list(objects)
    
    def get(self, **kwargs):
        """
        Retrieve an object definition.
        """
        uid = '{0}={1}'.format(self.uidf, kwargs.get(self.uidf, None))
        
        # Retrieving all
        if not kwargs:
            objects = self.model.objects.all()
            self.log('Retrieved all objects -> count={0}'.format(objects.count()), level='debug', method='get')
            return list(objects)
    
        # Object doesn't exist
        if not self.exists(**kwargs):
            self.log('Object not found -> filter={0}'.format(str(kwargs)), level='debug', method='get')
            return None
    
        # Get the object
        object = self.model.objects.get(**kwargs)
        self.log('Retrieved object: {0}'.format(uid), level='debug', method='get')
        return object