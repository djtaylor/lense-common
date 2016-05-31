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

        # Permissions model
        self.permissions = import_class('Permissions', 'lense.common.objects.permissions.models', init=False)

    def _count(self, **kwargs):
        """
        Find out how many objects would be returned by a query.
        """
        return self.model.objects.filter(**kwargs).count()
    
    def _process_object(self, obj, ref):
        """
        Process a single object appending to the reference object if accessible.
        
        :param obj: The object to process
        :type  obj: object
        :param ref: The reference object
        :type  ref: list
        """
        object_uuid = LENSE.OBJECTS.getattr(obj, 'uuid')
        
        # No UUID
        if not object_uuid:
            return ref.append(obj)
        
        # Disable permissions if bootstrapping
        if LENSE.bootstrap:
            self.log('Project is bootstrapping: return all objects', level='debug', method='_process_object')
            return ref.append(obj)
        
        # Get/set object permissions
        permissions = [LENSE.OBJECTS.dump(x) for x in list(self.permissions.objects.filter(object_uuid=object_uuid))]
        setattr(obj, '_permissions', permissions)
        
        # Log permissions
        get_permissions = 'Retrieved permissions: {0}({1}): {2}'.format(self.permissions.__name__, object_uuid, obj._permissions)
        if object_uuid:
            self.log(get_permissions, level='debug', method='_process_single')
            
        # Confirm access
        api_user   = LENSE.REQUEST.USER.uuid
        api_group  = LENSE.REQUEST.USER.group    
        access_str = 'User({0}::{1}) -> Object({2})'.format(api_user, api_group, object_uuid)
            
        # Object has no permissions, must be administrator
        if not obj._permissions:
            if api_group == GORUPS.ADMIN.UUID:
                return ref.append(obj)
            return None
            
        # Scan permissions
        for pr in obj._permissions:
            
            # Owner access
            if pr['owner'] == api_user:
                if pr['user_read']:
                    self.log('User read access granted {0}'.format(access_str), level='debug', method='_process_single')
                    
                    # User read access granted
                    return ref.append(obj)
                
            # Group access
            if pr['group'] == api_group:
                if pr['group_read']:
                    self.log('Group read access granted {0}'.format(access_str), level='debug', method='_process_single')
                    
                    # Group read access granted 
                    return ref.append(obj)
                
            # Read all access
            if pr['all_read']:
                self.log('Read all access granted {0}'.format(access_str), level='debug', method='_process_single')
                return ref.append(obj)
            
        # Access denied
        self.log('Access denied {0}'.format(access_str), level='debug', method='_process_single')
        return None
    
    def _process(self, objects):
        """
        Run a single or list of objects through internal filters.
        
        :param objects: A single or list of objects to process
        :type  objects: list|object
        :rtype: None|object|list
        """
        
        # Objects references
        objects_ref = []
        
        # Multiple objects
        if isinstance(objects, list):
            for obj in objects:
                self._process_object(obj, objects_ref)
            
        # Single object
        else:
            self._process_object(objects, objects_ref)
    
        # Return an objects
        return None if not objects_ref else (objects_ref if (len(objects_ref) > 1) else objects_ref[0])

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
        
    def get_internal(self, **kwargs):
        """
        Retrieve objects internally, bypassing the processing step.
        """
        
        # Total objects that would be retrieved
        object_count = self._count(**kwargs)
        
        # No objects found
        if object_count == 0:
            self.log('No objects found: filter={0}'.format(str(kwargs)), level='debug', method='get_internal')
            return None
        
        # Retrieve all objects
        if not kwargs:
            self.log('Retrieving all objects: count={0}, filter={1}'.format(str(object_count), str(kwargs)), level='debug', method='get_internal')
            return list(self.model.objects.all())
        
        # Multiple objects found
        if object_count > 1:
            self.log('Retrieving multiple objects: count={0}, filter={1}'.format(str(object_count), str(kwargs)), level='debug', method='get_internal')
            return list(self.model.objects.filter(**kwargs))
    
        # Single object found
        self.log('Retrieving single object: filter={0}'.format(str(kwargs)), level='debug', method='get_internal')
        return self.model.objects.get(**kwargs)
        
    def get(self, **kwargs):
        """
        Retrieve a single/multiple/all object models.
        """
        
        # Total objects that would be retrieved
        object_count = self._count(**kwargs)
        
        # No objects found
        if object_count == 0:
            self.log('No objects found: filter={0}'.format(str(kwargs)), level='debug', method='get')
            return None
        
        # Retrieve all objects
        if not kwargs:
            self.log('Retrieving all objects: count={0}, filter={1}'.format(str(object_count), str(kwargs)), level='debug', method='get')
            return self._process(list(self.model.objects.all()))
        
        # Multiple objects found
        if object_count > 1:
            self.log('Retrieving multiple objects: count={0}, filter={1}'.format(str(object_count), str(kwargs)), level='debug', method='get')
            return self._process(list(self.model.objects.filter(**kwargs)))
    
        # Single object found
        self.log('Retrieving single object: filter={0}'.format(str(kwargs)), level='debug', method='get')
        return self._process(self.model.objects.get(**kwargs))