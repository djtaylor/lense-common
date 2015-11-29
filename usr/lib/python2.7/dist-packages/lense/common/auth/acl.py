import json
import importlib

# Django Libraries
from django.contrib.auth.models import User

# Lense Libraries
from lense.common.http import HEADER, PATH
from lense.common.utils import valid, invalid
from lense.common.objects.group.models import APIGroups, APIGroupMembers
from lense.common.objects.handler.models import Handlers
from lense.common.objects.acl.models import ACLGlobalAccess, ACLObjectAccess, ACLKeys, ACLObjects
         
def get_obj_def(otype):
    """
    Retrieve the object definition for a specific type.
    
    :param    otype: The type of object to retrieve
    :type     otype: str
    :returns: ACL object model
    :rtype:   dict
    """
    return [x for x in list(ACLObjects.objects.all().values()) if x['type'] == otype][0]
         
class AuthACLObjects(object):
    """
    Parent class used to construct a list of objects that a user is authorized to access.
    """
    def __init__(self, otype, user=None, path=None, method=None):
        self.type      = otype
        
        # ACL user / request path / method
        self.user      = user if user else LENSE.REQUEST.USER.name
        self.path      = path if path else LENSE.REQUEST.path
        self.method    = method if method else LENSE.REQUEST.method
        
        # Get the ACL handler
        self.handler   = ACLHandler(self.path, self.method).get()
        
        # Object accessor
        self.obj_def   = get_obj_def(self.type)
        
        # Search filters
        self.filters   = {}
        
        # Object IDs / details
        self.ids       = []
        self.details   = []
        
    def extract(self, idstr):
        """
        Extract a specific object from the details list.
        """
        for i in self.details:
            if i[self.obj_def['obj_key']] == idstr:
                return i
        return None
        
    def _merge_objects(self, new_objs):
        """
        Merge a new list of objects with the existing object list, ignoring duplicate entries.
        """
        if isinstance(new_objs, list):
            for i in new_objs:
                if not (i[self.obj_def['obj_key']] in self.ids):
                    LENSE.LOG.info('Merging into objects list: {}'.format(str(i)))
                    self.ids.append(i[self.obj_def['obj_key']])
                    self.details.append(i)
        
    def _check_global_access(self, global_acls):
        """
        Determine if the user has global access to the handler.
        """
        for global_acl in global_acls:
            LENSE.LOG.info('Processing global ACL: {}'.format(str(global_acl)))
            
            # If access is explicitly denied, try another ACL
            if not global_acl['allowed'] == 'yes': continue
            
            # Get all supported global handlers for this ACL
            global_handlers = [x['handler_id'] for x in list(ACLGlobalAccess.objects.filter(acl=global_acl['uuid']).values())]
            LENSE.LOG.info('Retrieved handlers for ACL "{}": {}'.format(global_acl['acl'], str(global_handlers)))
            
            # If the ACL supports the target handler
            if self.handler.uuid in global_handlers:
                LENSE.LOG.info('Global access allowed for handler: cls={}, uuid={}'.format(self.handler.model.cls, self.handler.uuid))
                
                # Merge the object list
                self._merge_objects(LENSE.OBJECTS.get(self.type, filters=self.filters))
        
    def _check_object_access(self, object_acls, group):
        """
        Determine if the user has access to specific objects in the handler.
        """
        LENSE.LOG.info('Checking object access: group={}, objects={}'.format(group, str(object_acls)))
        
        # No handler object association
        if not self.handler.model.object:
            return
        
        # Create an instance of the ACL authorization class
        acl_mod   = importlib.import_module(self.obj_def['acl_mod'])
        acl_class = getattr(acl_mod, self.obj_def['acl_cls'])
        
        # Process each object ACL
        for object_acl in object_acls[self.type]['details']:
            LENSE.LOG.info('Processing object ACL: {}'.format(str(object_acl)))
            
            # ACL access filter
            acl_filter = { 'owner': group }
            acl_filter['acl_id']  = object_acl['acl_id']
            acl_filter['allowed'] = True
        
            # Begin constructing a list of accessible objects
            for access_object in list(acl_class.objects.filter(**acl_filter).values()):
                acl_key = '{}_id'.format(self.obj_def['acl_key'])
                LENSE.LOG.info('Object access allowed for handler: cls={}, uuid={}, object={}'.format(self.handler.model.cls, self.handler.uuid, str(access_object)))
                
                # Get the accessible object
                self._merge_objects(LENSE.OBJECTS.get(self.type, access_object[acl_key], filters=self.filters))
        
    def get(self, filters={}):
        """
        Process group membership and extract each object that is allowed for a specific group
        and ACL combination.
        """
        
        # Set any filters
        self.filters = filters
        LENSE.LOG.info('User ACLs: {}'.format(self.user.acls))
        
        # Process each group the user is a member of
        for group, acl in self.user.acls.iteritems():
        
            # Check for global access to the handler
            self._check_global_access(acl['global'])
        
            # Check for object level access to the handler
            self._check_object_access(acl['object'], group)
        
        # Return the authorized objects
        return self
         
class ACLHandler(object):
    """
    Parent class used to construct the ACL attributes for a specific handler. This includes
    retrieving the handler UUID, and any ACLs that provide access to this specific handler.
    """
    def __init__(self, path=None, method=None):
        
        # Handler name / UUID / object
        self.path   = path if path else LENSE.REQUEST.path
        self.method = method if method else LENSE.REQUEST.method
        self.model  = Handlers.objects.get(path=self.path, method=self.method)
        self.uuid   = self.model.uuid
        self.name   = self.model.name
        self.anon   = self.model.allow_anon
        
        # Log handler retrieval
        LENSE.LOG.info('Constructed API handler: name={0}, path={1}, method={2}, obj={3}, uuid={4}'.format(self.name, self.path, self.method, str(self.model), self.uuid))
                 
class ACLUser(object):
    """
    Parent class used to construct ACL attributes for a specific API user. Construct an object
    defining the username, groups the user is a member of, all ACLs the user has access to based
    on their groups, as well as the account type (i.e., user/host).
    """
    def __init__(self, user=None):
       
        # Username / groups / ACLs
        self.name   = user if user else LENSE.REQUEST.user.name
        self.groups = self._get_groups() 
        self.acls   = self._get_acls()
   
    def _get_acls(self):
        """
        Construct and return an object containing enabled ACLs for all groups the user
        is currently a member of.
        """
        acls = {}
        for group in self.groups:
            group_details = list(APIGroups.objects.filter(uuid=group).values())[0]
            acls[group] = {
                'object': group_details['permissions']['object'],
                'global': group_details['permissions']['global'],
            }
                
        # Return the ACLs object
        return acls
        
    def _get_groups(self):
        """
        Construct and return a list of group UUIDs that the current API user is a 
        member of.
        """
        
        # Get the user object
        _user = LENSE.USER.GET(username=self.name)
        
        # Construct a list of group UUIDs the user is a member of
        groups = [x['group_id'] for x in list(APIGroupMembers.objects.filter(member=_user.uuid).values())]
    
        # Log the user's group membership
        LENSE.LOG.info('Constructed group membership for user [{}]: {}'.format(_user.uuid, json.dumps(groups)))
        
        # Return the group membership list
        return groups
              
class AuthACLGateway(object):
    """
    ACL gateway class used to handle permissions for API requests prior to loading
    any API handlers. Used after key/token authorization.
    """
    def __init__(self, request=None):
        self.request       = request if request else LENSE.REQUEST
        
        # ACL handler / user
        self.handler       = ACLHandler()
        self.user          = None
        
        # Accessible objects / object key
        self.obj_list      = []
        self.obj_key       = None
        
        # Authorization flag / error container
        self.authorized    = False
        self.auth_error    = None
        
        # Authorize the request
        self._authorize()
        
    def _set_authorization(self, auth, err=None):
        """
        Set the authorized flag and an optional error message if the user is not authorized. Return the
        constructed ACL gateway instance.
        """
        self.authorized = auth
        self.auth_error = None if not err else err
        
        # Return the ACL gateway
        return self
        
    def _check_global_access(self, global_acls):
        """
        Determine if the user has global access to the handler.
        """
        for global_acl in global_acls:
            
            # If access is explicitly denied, try another ACL
            if not global_acl['allowed'] == 'yes': continue
            
            # Get all globally accessible handlers for this ACL
            global_access = [x['handler_id'] for x in list(ACLGlobalAccess.objects.filter(acl=global_acl['uuid']).values())]
            
            # If the ACL supports the target handler
            if self.handler.uuid in global_access:
                return valid(LENSE.LOG.info('Global access granted for user [{}] to handler [{}]'.format(self.user.name, self.handler.name)))
        
        # Global access denied
        return invalid('Global access denied for user [{}] to handler [{}]'.format(self.user.name, self.handler.name))
    
    def _check_object_access(self, object_acls, group):
        """
        Determine if the user has object level access to the handler.
        """
        
        # Make sure the handler has an object type association
        if not self.handler.model.object:
            return invalid('')
        object_type = self.handler.model.object
        
        # Get the object authorization class
        obj_def   = get_obj_def(object_type)
        acl_mod   = importlib.import_module(obj_def['acl_mod'])
        acl_class = getattr(acl_mod, obj_def['acl_cls'])
            
        # Utility object key and target object value
        self.obj_key = self.handler.model.object_key
        
        # Specific object key found
        if (self.request.data) and (self.obj_key in self.request.data):
            
            # Process each ACL for the object type
            tgt_obj = None
            for object_acl in object_acls[object_type]['details']:
                tgt_obj = self.request.data[self.obj_key]
            
                # Object filter
                filter = {}
                filter['owner']            = group
                filter['allowed']          = True
                filter[obj_def['acl_key']] = tgt_obj
            
                # Check if the user has access to this object
                if acl_class.objects.filter(**filter).count():
                    return valid(LENSE.LOG.info('Object level access granted for user [{}] to handler [{}] for object [{}:{}]'.format(self.user.name, self.handler.path, self.handler.model.object, tgt_obj)))
        
            # Access denied
            return invalid(' for object <{}:{}>'.format(self.handler.model.object, tgt_obj))
        
        # User not accessing a specific object
        else:
            return valid()
        
    def _check_access(self):
        """
        Make sure the user has access to the selected resource. Not sure how I want to handle a user 
        having multiple ACLs that provided access to the same handler. This raises the question on 
        what to do if one ACL is allowed, and another is disabled. I can either explicitly deny access 
        if any ACL is found with a disabled flag, or just skip the ACL and look for an enabled one. 
        For now I am going to do the latter.
        """    
        
        # Access status object
        group_access = {}
    
        # Look through each ACL grouping
        for group, acl_obj in self.user.acls.iteritems():
            
            # Group level access
            group_access[group] = {}
            
            # Check object and global access
            group_access[group] = {
                'global': self._check_global_access(acl_obj['global']),
                'object': self._check_object_access(acl_obj['object'], group)
            } 
            
        # Check the group access object
        obj_error  = ''
        can_access = False
        for group, access in group_access.iteritems():
            for type, status in access.iteritems():
                if status['valid']:
                    can_access = status
                
                # Capture any object errors
                if (type == 'object') and not (status['valid']):
                    obj_error = status['content']
        
        # Access allowed
        if can_access:
            return can_access
        
        # Access denied
        else:
            err_msg = 'Access denied to handler [{}]{}'.format(self.handler.name, obj_error)
            
            # Log the error message
            LENSE.LOG.error(err_msg)
            
            # Return the authentication error
            return invalid(err_msg)
        
    def _authorize(self):
        """
        Worker method used to make sure the API user has the appropriate permissions
        required to access the handler.
        """
        
        # Permit access to handlers which allow anonymous access
        if self.handler.anon:
            LENSE.LOG.info('Utility "{0}" allows anonymous access, approving request'.format(self.handler.name))
            return self._set_authorization(True)
        
        # Request is not anonymous, construct the user
        else:
            self.user = ACLUser(self.request.user).get()
        
        # Permit access to <auth/get> for all API users with a valid API key
        if self.handler.path == PATH.GET_TOKEN:
            return self._set_authorization(True)
            
        # Log the initial ACL authorization request
        LENSE.LOG.info('Running ACL gateway validation: name={0}, path={1}, method={2}, user={3}'.format(self.handler.name, self.handler.path, self.handler.method, self.user.name))
        
        # If the user is not a member of any groups (and not a host account type)
        if not self.user.groups and self.user.type == T_USER:
            return self._set_authorization(False, LENSE.LOG.error('User [{}] is not a member of any groups, membership required for handler authorization'.format(self.user.name)))
        
        # Check if the account has access
        try:
            access_status = self._check_access()
            if not access_status['valid']:
                return self._set_authorization(False, access_status['content'])
            LENSE.LOG.info('ACL gateway authorization success: name={0}, path={1}, method={2}, user={3}'.format(self.handler.name, self.handler.path, self.handler.method, self.user.name))
            
            # Account has access
            return self._set_authorization(True)
            
        # ACL gateway critical error
        except Exception as e:
            return self._set_authorization(False, LENSE.LOG.exception('Failed to run ACL gateway: {}'.format(str(e))))
    
    def target_object(self):
        """
        Public method used to extract the target object ID from the API data.
        """
        if self.request.data:
            _object = None if not (self.obj_key in self.request.data) else self.request.data[self.obj_key]
            
            # Log and return the object
            LENSE.LOG.info('Retrieved target object: {}'.format(str(_object)))
            return _object
        return None
        
    def authorized_objects(self, otype, path=None, method=None, filter=None):
        """
        Public method used to construct a list of authorized objects of a given type for the 
        API user.
        
        TODO: Need to filter out ACLs when doing the ACL object class to only include ACLs that apply for the
        current handler.
        
        :param otype:  The type of objects to retrieve
        :type  otype:  str
        :param path:   The API request path
        :type  path:   str
        :param method: The API request method
        :type  method: str
        :param filter: Optional object filters
        :type  filter: dict
        """
        path   = path if path else LENSE.REQUEST.path
        method = method if method else LENSE.REQUEST.method 
        
        # Create the authorized objects list
        return AuthACLObjects(
            user   = self.user, 
            otype  = otype, 
            path   = getattr(self.handler, 'path', path), 
            method = getattr(self.handler, 'method', method)
        ).get(filter)