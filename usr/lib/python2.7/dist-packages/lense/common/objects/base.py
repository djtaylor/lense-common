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
        self.logpre = '<OBJECTS:{0}> '.format(self.cls)

    def log(self, msg, level='info'):
        """
        Wrapper method for logging with a prefix.
        
        :param   msg: The message to log
        :type    msg: str
        :param level: The desired log level
        :type  level: str
        """
        logger = getattr(LENSE.LOG, level, 'info')
        logger('{0}{1}'.format(self.logpre, msg))

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

    def map_user(self, uid):
        """
        Map a username or UUID to kwargs dictionary.
        
        :param user: User name or UUID
        :type  user: str
        :rtype: dict
        """
        if self.is_uuid(uid):
            return {'uuid': uid}
        return {'username': uid}

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
        obj = self.get(**kwargs)
        uid = '{0}={1}'.format(self.uidf, getattr(kwargs, self.uidf))
        
        # Object doesn't exist, cannot updated
        if not obj:
            self.log('Cannot update object -> {0}: Does not exist'.format(uid), level='debug')
            return False
        
        # Update the object
        try:
            obj.update(**kwargs)
            self.log('Updated object -> {0}'.format(uid))
            return True
        
        # Failed to update object
        except Exception as e:
            self.log('Failed to update object -> {0}: {1}'.format(uid, str(e)), level='exception')
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
            self.log('Created object -> {0}'.format(uid), level='debug')
            
            # Return the new object
            return obj
        
        # Failed to create the object
        except Exception as e:
            self.log('Failed to create object: {0}'.format(self.cls, str(e)), level='exception')
            return False
    
    def delete(self, **kwargs):
        """
        Delete an object definition.
        """
        obj = self.get(**kwargs)
        uid = '{0}={1}'.format(self.uidf, kwargs.get(self.uidf, None))
        
        # Object doesn't exist, cannot delete
        if not obj:
            self.log('Cannot delete object -> {0}: Does not exist'.format(uid), level='debug')
            return False
        
        # Delete the object
        try:
            obj.delete()
            self.log('Deleted object -> {0}'.format(self.cls, uid), level='debug')
            return True

        # Failed to delete the object
        except Exception as e:
            self.log('Failed to delete object -> {0}: {1}'.format(self.cls, uid, str(e)), level='exception')
            return False
    
    def get(self, **kwargs):
        """
        Retrieve an object definition.
        """
        
        # Retrieving all
        if not kwargs:
            objects = self.model.objects.all()
            self.log('Retrieved all objects: count={1}'.format(self.cls, objects.count()), level='debug')
            return objects
    
        # Object doesn't exist
        if not self.exists(**kwargs):
            self.log('Object not found -> filter: {0}'.format(str(kwargs)), level='debug')
            return None
    
        # Retrieving by parameters
        object = self.model.objects.get(**kwargs)
        self.log('Retrieved object -> filter: {0}'.format(str(kwargs)), level='debug')
        return object