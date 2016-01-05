class AuthACLHandler(object):
    """
    Class object for storing ACL information related to the 
    target handler.
    """
    def __init__(self, path, method):
        self.object = LENSE.ensure(LENSE.OBJECTS.HANDLER.get(path=path, method=method),
            isnot = None,
            error = 'Could not retrieve handler for: path={0}, method={1}'.format(path, method),
            debug = 'Retrieved handler for ACL authorization: path={0}, method={1}'.format(path, method),
            code  = 404)
        
        # Store the handler UUID
        self.uuid   = self.object.uuid
        
        # Handler access
        self.access = {
            'object': LENSE.OBJECTS.ACL.ACCESS('object').filter(handler=self.object.uuid),
            'global': LENSE.OBJECTS.ACL.ACCESS('global').filter(handler=self.object.uuid) }
        
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
        LENSE.ensure(access_type in ['object', 'global'],
            error = 'Invalid access type: {0}'.format(access_type),
            code  = 500)
        self.access_type = access_type
  
class AuthACLGroup(object):
    """
    Class object for storing ACL information related to the 
    requesting group.
    """
    def __init__(self, group):
        self.object = LENSE.OBJECTS.GROUP.get(uuid=group)
        self.uuid   = self.object.uuid
        
        # Permissions
        self.permissions = {
            'object': LENSE.OBJECTS.ACL.PERMISSIONS('object').filter(owner=self.object.uuid),
            'global': LENSE.OBJECTS.ACL.PERMISSIONS('global').filter(owner=self.object.uuid) }
        
        # Access ACL UUIDs
        self.acls = {
            'object': [x.acl for x in self.permissions['object']],
            'global': [x.acl for x in self.permissions['global']] }
  
class AuthACLGateway(object):
    """
    Primary class for the request processor to interact with
    the ACL authorization backend.
    """
    def __init__(self):
        self.user     = LENSE.REQUEST.USER.name
        
        # Target handler / requesting group
        self.handler  = AuthACLHandler(LENSE.REQUEST.path, LENSE.REQUEST.method)
        self.group    = AuthACLGroup(LENSE.REQUEST.USER.group)
        
        # Gateway ready
        self.ready    = True
        
    def request(self):
        """
        Authorized group access to the request handler.
        """
        
        # Global / object access
        access_global = False
        access_object = False
        
        # Global access
        for acl in self.handler.acls['global']:
            if acl in self.group.acls['global']:
                self.handler.set_access('global')
                self.handler.set_acl(acl)
                access_global = True
        
        # No global access, try object
        if not access_global:
            for acl in self.handler.acls['object']:
                if acl in self.group.acls['object']:
                    self.handler.set_access('object')
                    self.handler.set_acl(acl)
                    access_object = True
        
        # Can the user access by either object or global level
        can_access = False if not (access_object or access_global) else True
        
        # Make sure the requesting group has some type of handler access
        LENSE.AUTH.ensure(can_access,
            error = 'No access granted for request handler',
            debug = 'Access granted to request handler: user={0}, group={1}, handler={2}, acl={3}'.format(self.user, self.group.uuid, self.handler.uuid, use_acl),
            code  = 401)
        
    def object(self, obj):
        """
        Confirm access to a single object.
        
        :param object: The object to check access for
        :type  object: mixed
        :rtype: obj|None
        """
        if self.disabled:
            return obj
        
        # User has global access to the handler
        if self.handler.access_type == 'global':
            return obj
        
        # Handler has not object association
        LENSE.ensure(self.handler.object_type,
            isnot = None,
            error = 'Cannot access, request handler has no ACL object type association',
            code  = 500)
        
        # Look for the object ID
        object_id = LENSE.ensure(getattr(obj, self.handler.object_key, False),
            isnot = False,
            error = 'Could not find object',
            code  = 404)
        
        # Look for an associated permissions object
        perms_object = LENSE.AUTH.ensure(LENSE.OBJECTS.ACL.PERMISSIONS('object').get(object_type=self.handler.object_type, object_id=object_id),
            isnot = None,
            error = 'Group does not have access to this object',
            code  = 401)
        
        # Make sure access is not explicitly disabled
        LENSE.AUTH.ensure(perms_object.allowed,
            isnot = False,
            error = 'Access to this object is disabled',
            code  = 401)
        
        # Access granted
        return obj
        
    def objects(self, objects):
        """
        Filter multiple objects.
        
        :param objects: The objects to filter through
        :type  objects: list
        :rtype: list|None
        """
        if self.disabled:
            return objects
        
        # User has global access to the handler
        if self.handler.access_type == 'global':
            return objects
         
        # Construct a list of accessible objects
        accessible_objects = []
        for obj in objects:
            try:
                accessible_objects.append(self.object(obj))
            except:
                pass
        return accessible_objects

    @classmethod
    def enable(cls):
        """
        Static method for enabling the ACL gateway. 
        """
        LENSE.AUTH.ACL = cls()