from lense import import_class
from lense.common.exceptions import AuthError

class AuthInterface(object):
    """
    Lense authentication interface.
    """
    def __init__(self):
        self._key    = import_class('AuthAPIKey', 'lense.common.auth.key', init=False)
        self._token  = import_class('AuthAPIToken', 'lense.common.auth.token', init=False)
        self._portal = import_class('AuthPortal', 'lense.common.auth.portal', init=False)
        
        # ACL gateway
        self.ACL     = None
        
        # Store the authentication error
        self._error  = None
        
    def get_error(self):
        """
        Return any authentication errors
        """
        return self._error
    
    def set_error(self, msg):
        """
        Set the most recent error message.
        
        :param msg: The error message to store
        :type  msg: str
        :rtype: bool
        """
        self._error = LENSE.LOG.error(msg)
        return False
    
    def set_acl(self, request, override=None):
        """
        Run the ACL gateway.
        
        :param  request: The Lense request object
        :type   request: LenseRequestObject
        :param override: Override any built in authorization methods
        :type  override: bool | True (allow all) False (allow none)
        """
        self.ACL = import_class('AuthACLGateway', 'lense.common.auth.acl', args=[request, override])
    
    def KEY(self, user, key):
        """
        Wrapper method for performing key based authentication.
        
        :param user: The user to authenticate
        :type  user: str
        :param  key: The API request key
        :type   key: str
        """
        try:
            return self._key.validate(user, key)
        except AuthError as e:
            return self.set_error(str(e))
    
    def TOKEN(self, user, token):
        """
        Wrapper method for performing token based authentication.
        
        :param  user: The user to authenticate
        :type   user: str
        :param token: The API request token
        :type  token: str
        """
        try:
            return self._token.validate(user, token)
        except AuthError as e:
            return self.set_error(str(e))
        
    def PORTAL(self, user, passwd):
        """
        Wrapper method for performing portal authentication.
        
        :param   user: The user to authenticate
        :type    user: str
        :param passwd: The reques password
        :type  passwd: str
        """
        try:
            return self._portal.validate(user, passwd)
        except AuthError as e:
            return self.set_error(str(e))