from copy import copy
from uuid import UUID

# Django Libraries
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# Lense Libraries
from lense import import_class
from lense.common.vars import GROUPS
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

        # Debug log prefix
        self.logpre   = 'OBJECTS:{0}'.format(self.cls)

        # Selected object
        self.selected = None

    def _count(self, **kwargs):
        """
        Find out how many objects would be returned by a query.
        """
        return self.model.objects.filter(**kwargs).count()
        
    def _process_read(self, objects):
        """
        Process read requests for objects.
        
        :param objects: A single or list of objects to process
        :type  objects: list|object
        :rtype: None|object|list
        """
        
        # Objects references
        objects_ref = []
        
        # Multiple objects
        if isinstance(objects, list):
            for obj in objects:
                if LENSE.PERMISSIONS.can_read(obj):
                    objects_ref.append(obj)
            
        # Single object
        else:
            if LENSE.PERMISSIONS.can_read(objects):
                objects_ref.append(objects)
    
        # Return an objects
        return None if not objects_ref else (objects_ref if (len(objects_ref) > 1) else objects_ref[0])

    def _process_delete(self, objects):
        """
        
        """
        
        # Multiple objects
        if isinstance(objects, list):
            for obj in objects:
                if LENSE.PERMISSIONS.can_delete(obj):
                    
                    # Flush permissions
                    LENSE.OBJECTS.PERMISSIONS.flush(obj)
                    
                    # Delete the object
                    obj.delete()
                    self.log('Deleted object -> {0}'.format(repr(obj)), level='debug', method='_process_delete')
            
        # Single object
        else:
            if LENSE.PERMISSIONS.can_delete(objects):
                
                # Flush permissions
                LENSE.OBJECTS.PERMISSIONS.flush(objects)
                
                # Delete the object
                obj.delete()
                self.log('Deleted object -> {0}'.format(repr(objects)), level='debug', method='_process_delete')

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
        
        # No object selected
        if not self.selected:
            self.log('Cannot perform update, no object(s) selected')
        
        # Update the object
        try:
            for k,v in kwargs.iteritems():
                setattr(self.selected, k, v)
            self.selected.save()
            self.log('Updated object -> {0}'.format(repr(self.selected)), level='debug', method='update')
            
            # Deselect the object
            self.selected = None
            return True
        
        # Failed to update object
        except Exception as e:
            self.log('Failed to update object -> {0}: {1}'.format(repr(self.selected), str(e)), level='exception', method='update')
            
            # Deselect the object
            self.selected = None
            return False
    
    def create(self, **kwargs):
        """
        Create a new object
        """
        try:
            
            # Override permissions
            permissions = {}
            if 'permissions' in kwargs:
                permissions = copy(kwargs['permissions'])
                del kwargs['permissions']
            
            # Create/save the object
            obj = self.model(**kwargs)
            obj.save()
            self.log('Created object -> {0}'.format(repr(obj)), level='debug', method='create')
            
            # Create object permissions
            LENSE.OBJECTS.PERMISSIONS.create(obj, permissions)
            
            # Return the new object
            return obj
        
        # Failed to create the object
        except Exception as e:
            self.log('Failed to create object -> {0}'.format(str(e)), level='exception', method='create')
            return False
          
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
        
    def _get(self, process, **kwargs):
        """
        Internal method for retrieving objects from the database.
        
        :param process: Whether to process the objects through permissions filters
        :type  process: bool
        """
        
        # Total objects that would be retrieved / objects retrieved
        count   = self._count(**kwargs)
        objects = None
        
        # No objects found
        if object_count == 0:
            self.log('No objects found: filter={0}'.format(str(kwargs)), level='debug', method='_get')
            return None
        
        # Retrieve all objects
        if not kwargs:
            self.log('Retrieving all objects: count={0}, filter={1}'.format(str(count), str(kwargs)), level='debug', method='_get')
            objects = list(self.model.objects.all())
        
        # Multiple objects found
        if object_count > 1:
            self.log('Retrieving multiple objects: count={0}, filter={1}'.format(str(count), str(kwargs)), level='debug', method='_get')
            objects = list(self.model.objects.filter(**kwargs))
    
        # Single object
        if object_count == 1:
            self.log('Retrieving single object: filter={0}'.format(str(kwargs)), level='debug', method='_get')
            objects = self.model.objects.get(**kwargs)
    
        # Return and optionally process objects
        return objects if not process else self._process_read(objects)

    def _delete(self, process, **kwargs):
        """
        Internal method for deleting objects from the database.
        
        :param process: Whether to process the objects through permissions filters
        :type  process: bool
        """
        
        # Get any available objects
        objects = self.get(**kwargs) if process else self.get_internal(**kwargs)
        
        # No objects retrieved
        if not objects:
            self.log('Cannot delete, no objects found: filter={0}'.format(**kwargs), level='_debug', method='_delete')
            return False
        
        # Process delete operation
        if process:
            return self._process_delete(objects)
        
        # Delete internal
        else:
            try:
                
                # List of objects
                if isinstance(objects, list):
                    for obj in objects:
                        
                        # Flush permissions
                        LENSE.OBJECTS.PERMISSIONS.flush(obj)
                        
                        # Delete the object
                        self.log('Deleting object -> {0}'.format(repr(obj)), level='debug', method='_delete')
                        obj.delete()
                    
                # Single object
                else:
                    
                    # Flush permissions
                    LENSE.OBJECTS.PERMISSIONS.flush(obj)
                    
                    # Delete the object
                    self.log('Deleting object -> {0}'.format(repr(obj)), level='debug', method='_delete')
                    obj.delete()
                
            # Delete operation(s) failed
            except Exception as e:
                self.log('Failed to delete object(s): filter={0}: {1}'.format(str(kwargs), str(e)), level='exception', method='_delete')
                return False
        
    def get_internal(self, **kwargs):
        """
        Retrieve objects internally, bypassing the processing step.
        """
        return self._get(False, **kwargs)
        
    def get(self, **kwargs):
        """
        Retrieve a single/multiple/all object models.
        """
        return self._get(True, **kwargs)
    
    def delete_internal(self, **kwargs):
        """
        Delete objects and bypass permissions.
        """
        return self._delete(False, **kwargs)
        
    def delete(self, **kwargs):
        """
        Delete objects after performing permissions checks.
        """
        return self._delete(True, **kwargs)