import ldap
import json

# Django Libraries
from django_auth_ldap.config import LDAPSearch, LDAPSearchUnion

# Lense Libraries
import lense.common.config as config

# Configuration
CONFIG = config.parse('SERVER')

class AuthGroupsLDAP(object):
    """
    Construct an LDAPSearchUnion object for every LDAP search group defined.
    """
    
    @staticmethod
    def get_map():
        """
        Load the LDAP JSON map file.
        """
        try:
            return json.load(open(CONFIG.ldap.map))
        
        # Failed to parse JSON map file
        except Exception as e:
            raise Exception('Failed to load LDAP JSON map file [{}]: {}'.format(CONFIG.ldap.map, str(e)))
    
    @staticmethod
    def construct():
        """
        Construct the LDAP search union.
        """
        if CONFIG.auth.backend == 'ldap':

            # Define the search union
            search_union = []
            
            # Get the LDAP map
            map = AuthGroupsLDAP.get_map()
            
            # Process each group definition
            for ldap_group in map['groups']:
                search_union.append(LDAPSearch(ldap_group['tree'], ldap.SCOPE_SUBTREE, "(" + ldap_group['uid_attr'] + "=%(user)s)"))

            # Return the LDAPSearchUnion object
            return LDAPSearchUnion(*search_union)