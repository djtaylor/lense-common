from re import compile
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
        self.ACL     = import_class('AuthACLGateway', 'lense.common.auth.acl', init=False)
        
    def check_pw_strength(self, passwd):
        """
        Make sure a password meets strength requirements.
        """
        regex = compile(r'^\S*(?=\S{8,})(?=\S*[a-z])(?=\S*[A-Z])(?=\S*[\d])(?=\S*[\W])\S*$')
        if not regex.match(passwd):
            return False
        return True
        
    def ensure(self, *args, **kwargs):
        """
        Raise an AuthError if ensure fails.
        """
        kwargs['exc'] = AuthError
        return LENSE.ensure(*args, **kwargs)
    
    def KEY(self, user, key):
        """
        Wrapper method for performing key based authentication.
        
        :param user: The user to authenticate
        :type  user: str
        :param  key: The API request key
        :type   key: str
        """
        return self._key.validate(user, key)
    
    def TOKEN(self, user, token):
        """
        Wrapper method for performing token based authentication.
        
        :param  user: The user to authenticate
        :type   user: str
        :param token: The API request token
        :type  token: str
        """
        return self._token.validate(user, token)
        
    def PORTAL(self, user, passwd):
        """
        Wrapper method for performing portal authentication.
        
        :param   user: The user to authenticate
        :type    user: str
        :param passwd: The reques password
        :type  passwd: str
        """
        return self._portal.validate(user, passwd)