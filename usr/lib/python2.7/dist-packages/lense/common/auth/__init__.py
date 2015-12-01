from lense.common.auth.key import AuthAPIKey
from lense.common.auth.acl import AuthACLGateway
from lense.common.auth.token import AuthAPIToken
from lense.common.auth.portal import AuthPortal
from lense.common.exceptions import AuthError

class AuthInterface(object):
    """
    Lense authentication interface.
    """
    def __init__(self):
        self._key    = AuthAPIKey
        self._token  = AuthAPIToken
        self._portal = AuthPortal
        
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
    
    def set_acl(self, request):
        """
        Run the ACL gateway.
        
        :param request: The Lense request object
        :type  request: LenseRequestObject
        """
        self.ACL = AuthACLGateway(request)
    
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