# Django Libraries
from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_backends, get_user_model

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger
from cloudscape.common.utils import rstring
from cloudscape.common.auth.utils import AuthGroupsLDAP

# Configuration / logger
CONFIG = config.parse()
LOG    = logger.create(__name__, CONFIG.utils.log)
                
class AuthBackendLDAP(LDAPBackend):
    """
    Class wrapper for querying the LDAP server for authentication.
    """ 
    def __init__(self):
        super(AuthBackendLDAP, self).__init__()
    
        # Get the LDAP JSON map object
        self.map = AuthGroupsLDAP.get_map()
    
    def _map_user_attrs(self, ldap_attrs):
        """
        Map LDAP user attributes to database user attributes.
        """
        
        # Mapped attributes
        mapped = {}
        
        # Map each database attribute
        for d,l in CONFIG.ldap_attr._asdict().iteritems():
            mapped[d] = ldap_attrs[l][0]
        
        # Return the mapped attributes
        return mapped
    
    def authenticate(self, username, password):
        """
        Authenticate the user and store the encrypted password for default database authentication.
        """
        user = super(AuthBackendLDAP, self).authenticate(username, password)
    
        # If the user authentication succeeds, save the password in Django
        if user:
            user.set_password(password)
            user.save()
            
        # Return the authenticated user object
        return user
    
    def get_or_create_user(self, username, ldap_user):
        """
        Retrieve or create a user account.
        """
        
        LOG.info('LDAP_USER_DN: %s' % str(ldap_user.dn))
        LOG.info('LDAP_USER_ATTRS: %s' % str(ldap_user.attrs))
        
        # Map the user attributes
        user_attrs = self._map_user_attrs(ldap_user.attrs)
        
        # Add extra database attributes. Generate a random password (will be changed during authentication)
        user_attrs.update({
            'from_ldap': True,
            'password':  rstring()
        })
        
        # Get the user model
        user_model = get_user_model()
        
        # Get or create the user model and then return
        return user_model.objects.get_or_create(**user_attrs)
    
class AuthBackendInterface(ModelBackend):
    """
    Custom authentication backend to provided mixed database/LDAP support depending on the 
    server configuration.
    """
    def __init__(self):
        
        # Get the usermodel
        self.user_model = get_user_model()
    
    def _user_from_ldap(self, username):
        """
        Check if the user is pulled from the LDAP server.
        """
        if self.user_model.objects.filter(username=username).count():
            return self.user_model.objects.get(username=username).from_ldap
        return None
    
    def _authenticate_ldap(self, username, password):
        """
        Wrapper method for handling LDAP authentication.
        """
        
        # Log the authentication attempt
        LOG.info('Attempting LDAP authentication for user [%s]' % username)
        
        # Try to authenticate the user
        try:
            auth_status = AuthBackendLDAP().authenticate(username, password)
            
            # Log the authentication status
            if auth_status:
                LOG.info('LDAP authentication status for user [%s]: authenticated=%s' % (auth_status.username, repr(auth_status.is_authenticated())))
            else:
                LOG.error('LDAP authentication failed for user [%s]' % username)
                
                # Fallback to database authentication if possible
                return self._authenticate_database(username, password, allow_ldap=True)
            
            # Return the authentication status
            return auth_status
            
        # Fallback to database authentication
        except Exception as e:
            LOG.exception('LDAP authentication failed for user [%s]: %s' % (username, str(e)))
            
            # Return the database authentication object
            return self._authenticate_database(username, password, allow_ldap=True)
    
    def _authenticate_database(self, username, password, allow_ldap=False):
        """
        Wrapper method for handling default database authentication.
        """
        
        # Get the user object
        user_obj = self.user_model.objects.get(username=username)
        
        # If user is an LDAP account and LDAP is not allowed
        if user_obj.from_ldap and not allow_ldap:
            LOG.info('Database authentication failed for user [%s], account is from LDAP and [allow_ldap = %s]' % (username, repr(allow_ldap)))
            return None
        
        # Log the authentication attempt
        LOG.info('Attempting database authentication for user [%s]' % username)
        
        # Attempt to authenticate the user
        auth_status = ModelBackend.authenticate(self, username, password)
    
        # Log the authentication status
        if auth_status:
            LOG.info('Database authentication status for user [%s]: authenticated=%s' % (auth_status.username, repr(auth_status.is_authenticated())))
        else:
            LOG.error('Database authentication failed for user [%s]' % username)
            
        # Return the authentication status
        return auth_status
    
    def authenticate(self, username=None, password=None):
        """
        Authenticate a username/password combination.
        """
        
        # If LDAP authentication is configured
        if CONFIG.auth.backend == 'ldap':
            
            # If the user doesn't exist
            if not self.user_model.objects.filter(username=username).count():
                
                # Attempt user authentication
                return self._authenticate_ldap(username, password)
            
            # If the user is from LDAP
            if self._user_from_ldap(username):
                return self._authenticate_ldap(username, password)
                
            # User is not an LDAP account
            else:
                return self._authenticate_database(username, password)
        
        # Using database authentication
        else:
            return self._authenticate_database(username, password)