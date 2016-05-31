from lense.common.auth import AuthBase

class AuthACLHandler(AuthBase):
    """
    Class object for storing ACL information related to the 
    target handler.
    """
    def __init__(self, path, method):
        super(AuthACLHandler, self).__init__()
        
        # ACL handler attributes
        self.object      = None
        self.uuid        = None
        self.access      = None
        self.acls        = None
        
        # Access type / access ACL
        self.access_type = None
        self.access_acl  = None
        
        # Object type / key
        self.object_type = None
        self.object_key  = None
        
        # Construct the ACL handler
        self._construct()
        
    def _construct(self):
        """
        Private method for constructing the ACL handler object.
        """
        
        # ACL gateway disabled
        if not LENSE.AUTH.ACL.enabled:
            return True
        
        # Handler object
        self.object = self.ensure(LENSE.OBJECTS.HANDLER.get(path=path, method=method),
            isnot = None,
            error = 'Could not retrieve handler for: path={0}, method={1}'.format(path, method),
            debug = 'Retrieved handler for ACL authorization: path={0}, method={1}'.format(path, method),
            code  = 404)
        
        # Store the handler UUID
        self.uuid   = self.object.uuid
        
        # Handler access
        self.access = {
            'object': LENSE.OBJECTS.ACL.ACCESS('object').get(handler=self.object.uuid),
            'global': LENSE.OBJECTS.ACL.ACCESS('global').get(handler=self.object.uuid) }
        
        # Access ACL UUIDs
        self.acls = {
            'object': [x.acl for x in self.access['object']],
            'global': [x.acl for x in self.access['global']] }
  
        # Handler access type / access ACL
        self.access_type = None
        self.access_acl  = None
  
        # Object type and key
        self.object_type = self.object.object
        self.object_key  = self.object.object_key
  
    def set_acl(self, acl):
        """
        Set the active ACL used to access the request handler.
        
        :param acl: The ACL UUID
        :type  acl: str
        """
        self.access_acl = acl
  
    def set_access(self, access_type):
        """
        Set the handler access type.
        
        :param access_type: Either object or global access
        :type  access:type:
        """
        self.ensure(access_type in ['object', 'global'],
            error = 'Invalid access type: {0}'.format(access_type),
            code  = 500)
        self.access_type = access_type
  
class AuthACLGroup(AuthBase):
    """
    Class object for storing ACL information related to the 
    requesting group.
    """
    def __init__(self, group):
        super(AuthACLGroup, self).__init__()
        
        # ACL group attributes
        self.object      = None
        self.uuid        = None
        self.permissions = None
        self.acls        = None
        
        # Construct ACL groups
        self._construct()
        
    def _construct(self):
        """
        Private method for constructing ACL groups if the ACL gateway is enabled.
        """
        
        # ACL gateway disabled
        if not LENSE.AUTH.ACL.enabled:
            return True
        
        # Group object / UUID
        self.object = self.ensure(LENSE.OBJECTS.GROUP.get(uuid=group),
            isnot = None,
            error = 'Could not find group: {0}'.format(group),
            code  = 404)
        self.uuid   = self.object.uuid
        
        # Permissions
        self.permissions = {
            'object': LENSE.OBJECTS.ACL.PERMISSIONS('object').get(owner=self.object.uuid),
            'global': LENSE.OBJECTS.ACL.PERMISSIONS('global').get(owner=self.object.uuid) }
        
        # Access ACL UUIDs
        self.acls = {
            'object': [x.acl for x in self.permissions['object']],
            'global': [x.acl for x in self.permissions['global']] }
  
class AuthACLGateway(AuthBase):
    """
    Primary class for the request processor to interact with
    the ACL authorization backend.
    """
    
    # ACL enabled/disabled flag / anonymous flag
    enabled   = LENSE.CONF.auth.acl
    anonymous = LENSE.REQUEST.is_anonymous
    
    def __init__(self):
        super(AuthACLGateway, self).__init__()
        self.user     = LENSE.REQUEST.USER.name
        
        # Target handler / requesting group
        self.handler  = AuthACLHandler(LENSE.REQUEST.path, LENSE.REQUEST.method)
        self.group    = AuthACLGroup(LENSE.REQUEST.USER.group)
        
    @classmethod
    def request(cls):
        """
        Authorized group access to the request handler.
        """
        
        # Is the ACL gateway enabled
        if not LENSE.AUTH.ACL.enabled:
            return LENSE.AUTH.ACL.log('ACL gateway disabled - granting access to handler', level='debug')
        
        # Global / object access
        access_global = False
        access_object = False
        
        # Global access
        for acl in LENSE.AUTH.ACL.handler.acls['global']:
            if acl in LENSE.AUTH.ACL.group.acls['global']:
                LENSE.AUTH.ACL.handler.set_access('global')
                LENSE.AUTH.ACL.handler.set_acl(acl)
                access_global = True
        
        # No global access, try object
        if not access_global:
            for acl in LENSE.AUTH.ACL.handler.acls['object']:
                if acl in LENSE.AUTH.ACL.group.acls['object']:
                    LENSE.AUTH.ACL.handler.set_access('object')
                    LENSE.AUTH.ACL.handler.set_acl(acl)
                    access_object = True
        
        # Can the user access by either object or global level
        can_access = False if not (access_object or access_global) else True
        
        # Debug log attributes
        debug_attrs = [LENSE.AUTH.ACL.user, LENSE.AUTH.ACL.group.uuid, LENSE.AUTH.ACL.handler.uuid, LENSE.AUTH.ACL.handler.access_acl]
        
        # Make sure the requesting group has some type of handler access
        LENSE.AUTH.ACL.ensure(can_access,
            error = 'No access granted for request handler',
            debug = 'Access granted to request handler: user={0}, group={1}, handler={2}, acl={3}'.format(*debug_attrs),
            code  = 401)
        
    @classmethod
    def _object(cls, obj):
        """
        Confirm access to a single object.
        
        :param object: The object to check access for
        :type  object: mixed
        :rtype: obj|None
        """
        
        # User has global access to the handler
        if LENSE.AUTH.ACL.handler.access_type == 'global':
            return obj
        
        # Handler has not object association
        LENSE.AUTH.ACL.ensure(LENSE.AUTH.ACL.handler.object_type,
            isnot = None,
            error = 'Cannot access, request handler has no ACL object type association',
            code  = 500)
        
        # Look for the object ID
        object_id = LENSE.AUTH.ACL.ensure(getattr(obj, LENSE.AUTH.ACL.handler.object_key, False),
            isnot = False,
            error = 'Could not find object',
            code  = 404)
        
        # Look for an associated permissions object
        perms_object = LENSE.AUTH.ACL.ensure(LENSE.OBJECTS.ACL.PERMISSIONS('object').get(object_type=LENSE.AUTH.ACL.handler.object_type, object_id=object_id),
            isnot = None,
            error = 'Group does not have access to this object',
            code  = 401)
        
        # Make sure access is not explicitly disabled
        LENSE.AUTH.ACL.ensure(perms_object.allowed,
            isnot = False,
            error = 'Access to this object is disabled',
            code  = 401)
        
        # Access granted
        return obj
        
    @classmethod
    def objects(cls, objects):
        """
        Filter multiple objects.
        
        :param objects: The object(s) to filter through
        :type  objects: object|list
        :rtype: object|list|None
        """
        
        # ACL gateway disabled
        if not LENSE.AUTH.ACL.enabled:
            LENSE.AUTH.ACL.log('ACL gateway disabled - granting access to all objects', level='debug')
            return objects
        
        # User has global access to the handler
        if LENSE.AUTH.ACL.handler.access_type == 'global':
            return objects
        
        # Single object
        if not isinstance(objects, list):
            try:
                return LENSE.AUTH.ACL._object(objects)
            except:
                return None
         
        # Construct a list of accessible objects
        accessible_objects = []
        for obj in objects:
            try:
                accessible_objects.append(LENSE.AUTH.ACL._object(obj))
            except:
                pass
        return accessible_objects

    @classmethod
    def enable(cls):
        """
        Static method for enabling the ACL gateway. 
        """
        
        # Initialize the gateway
        LENSE.AUTH.ACL = cls()
        
        # Disabled via configuration
        if not cls.enabled:
            return LENSE.AUTH.ACL.log('ACL gateway administratively disabled: conf.auth.acl = {0}'.format(repr(cls.enabled)))
        
        # Anonymous request
        if cls.anonymous:
            return LENSE.AUTH.ACL.log('ACL gateway disabled for anonymous request')
        
        # Enable the ACL gateway
        LENSE.AUTH.ACL.log('Enabling ACL gateway')
        LENSE.AUTH.ACL.enabled = True