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
        self.module   = mod
        self.cls      = cls
        
        # Get the object model / unique ID field
        self.model    = import_class(cls, mod, init=False)
        self.uidf     = getattr(self.model, 'UID_FIELD', self.cls)

        # ACL authorization flag / object dump / object counter
        self.use_acl  = False
        self.use_dump = False
        self.count    = False

        # Debug log prefix
        self.logpre   = 'OBJECTS:{0}'.format(self.cls)

        # Selected object
        self.selected = None

    def _process(self, objects):
        """
        Process and return queried objects depending on internal flags.
        
        :param objects: The object(s) to filter
        :type  objects: object|list
        :rtype: object|list
        """
        
        # ACL / object dump filters
        objects = objects if not self.use_acl else LENSE.AUTH.ACL.objects(objects)
        objects = objects if not self.use_dump else LENSE.OBJECTS.dump(objects)
            
        # Reset the internal flags
        self.use_acl  = False
        self.use_dump = False
    
        # Return the processed object(s)
        return objects

    def set(self, acl=False, dump=False):
        """
        Set internal flags prior to querying and returning results.
        
        :param  acl: Filter results through the ACL gateway
        :type   acl: bool
        :param dump: Dump results to a dictionary
        :type  dump: bool
        :rtype: self
        """
        if hasattr(LENSE.AUTH.ACL, 'ready'):
            self.use_acl = acl
        self.use_dump = dump
        return self

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
        logger('<{0}{1}:{2}@{3}> {4}'.format(
            self.logpre, 
            '' if not method else '.{0}'.format(method), 
            LENSE.REQUEST.USER.name,
            LENSE.REQUEST.client,
            msg
        ))

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

    def _count(self, **kwargs):
        """
        Find out how many objects would be returned by a query.
        """
        return self.model.objects.filter(**kwargs).count()

    def exists(self, **kwargs):
        """
        Check if an object exists.
        """
        count = self._count(**kwargs)
        self.log('Found {0} object(s) -> filter={1}'.format(str(count), str(kwargs)), level='debug', method='exists')
        return count
    
    def update(self, **kwargs):
        """
        Update a selected object object.
        """
        uid = '{0}={1}'.format(self.uidf, kwargs.get(self.uidf, None))
        
        # No object selected
        if not self.selected:
            self.log('Cannot perform update, no object(s) selected')
        
        # Update the object
        try:
            for k,v in kwargs.iteritems():
                setattr(self.selected, k, v)
            self.selected.save()
            self.log('Updated object -> {0}'.format(uid), level='debug', method='update')
            
            # Deselect the object
            self.selected = None
            return True
        
        # Failed to update object
        except Exception as e:
            self.log('Failed to update object -> {0}: {1}'.format(uid, str(e)), level='exception', method='update')
            
            # Deselect the object
            self.selected = None
            return False
    
    def create(self, **kwargs):
        """
        Create a new object
        """
        try:
            
            # Create/save the object
            obj = self.model(**kwargs)
            obj.save()
            uid = '{0}={1}'.format(self.uidf, getattr(obj, self.uidf, None))
            self.log('Created object -> {0}'.format(uid), level='debug', method='create')
            
            # Create object permissions
            LENSE.OBJECTS.PERMISSIONS.create(obj)
            
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
        self.log('Retrieved objects -> count={0}, lfilter={1}'.format(objects.count(), str(kwargs)), level='debug', method='filter')
        
        # Process and return the object(s)
        return self._process(list(objects))
    
    def _filter(self, **kwargs):
        return self.filter(**kwargs)
    
    def select(self, **kwargs):
        """
        Select an object before running an update.
        """
        self.selected = self.get(**kwargs)
        
        # No object found
        if not self.selected:
            raise RequestError(self.log('Could not locate object <{0}>: filter={1}'.format(self.cls, kwargs)), code=404)
        
        # Cannot select multiple objects
        if isinstance(self.selected, list):
            raise RequestError(self.log('Selection of multiple <{0}> objects not supported: found={1}'.format(self.cls, str(len(self.selected)))))
        
        # Log object selected
        self.log('Selected object <{0}>: {1}'.format(self.cls, ', '.join(['{0}={1}'.format(k,v) for k,v in kwargs.iteritems()])))
        
        # Return the base object handler
        return self
    
    def get(self, **kwargs):
        """
        Retrieve an object definition.
        """
        uid = '{0}={1}'.format(self.uidf, kwargs.get(self.uidf, None))
        
        # Retrieving all
        if not kwargs:
            objects = self.model.objects.all()
            self.log('Retrieved all objects -> count={0}'.format(objects.count()), level='debug', method='get')
            
            # Process and return the objects
            return self._process(list(objects))
        
        # Redirect to filter method if multiple objects found
        if self._count(**kwargs) > 1:
            self.log('Multiple objects found, redirect -> filter()', level='debug', method='get')
            return self._filter(**kwargs)
    
        # Object doesn't exist
        if not self.exists(**kwargs):
            self.log('Object not found -> filter={0}'.format(str(kwargs)), level='debug', method='get')
            return None
    
        # Get the object
        obj = self.model.objects.get(**kwargs)
        self.log('Retrieved object: {0}'.format(uid), level='debug', method='get')
        
        # Process and return the object
        return self._process(obj)