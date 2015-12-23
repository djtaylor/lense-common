from copy import copy
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
        
        # Get the object model / primary key
        self.model  = import_class(cls, mod, init=False)
        self.pk     = self.model._meta.pk.name

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
        uid = '{0}={1}'.format(self.pk, getattr(kwargs, self.pk))
        
        # Object doesn't exist, cannot updated
        if not obj:
            LENSE.LOG.debug('Cannot update <{0}> object <{1}>, does not exist'.format(self.cls, uid))
            return False
        
        # Update the object
        try:
            obj.update(**kwargs)
            return True
        
        # Failed to update object
        except Exception as e:
            LENSE.LOG.exception('Failed to update <{0}> object <{1}>: {2}'.format(self.cls, uid, str(e)))
    
    def create(self, **kwargs):
        """
        Create a new object
        """
        uid = '{0}={1}'.format(self.pk, getattr(kwargs, self.pk))
        try:
            
            # Create/save the object
            obj = self.model(**params)
            obj.save()
            LENSE.LOG.debug('Created <{0}> object <{1}>'.format(self.cls, uid))
            
            # Return the new object
            return obj
        
        # Failed to create the object
        except Exception as e:
            LENSE.LOG.exception('Failed to create <{0}> object <{1}>: {2}'.format(self.cls, uid, str(e)))
            return False
    
    def delete(self, **kwargs):
        """
        Delete an object definition.
        """
        obj = self.get(**kwargs)
        uid = '{0}={1}'.format(self.pk, kwargs.get(self.pk, None))
        
        # Object doesn't exist, cannot delete
        if not obj:
            LENSE.LOG.debug('Cannot delete <{0}>, object <{1}> does not exist'.format(self.cls, uid))
            return False
        
        # Delete the object
        try:
            obj.delete()
            LENSE.LOG.debug('Deleted <{0}> object <{1}>'.format(self.cls, uid))
            return True

        # Failed to delete the object
        except Exception as e:
            LENSE.LOG.exception('Failed to delete <{0}> object <{1}>: {2}'.format(self.cls, uid, str(e)))
            return False
    
    def get(self, **kwargs):
        """
        Retrieve an object definition.
        """
        
        # Retrieving all
        if not kwargs:
            objects = self.model.objects.all()
            LENSE.LOG.debug('Retrieved all <{0}> objects -> count: {1}'.format(self.cls, len(objects)))
            return objects
    
        # Retrieving by parameters
        objects = self.model.objects.get(**kwargs)
        LENSE.LOG.debug('Retrieved <{0}> objects -> count: {1}, filter: {2}'.format(self.cls, len(objects), str(kwargs)))
        return objects