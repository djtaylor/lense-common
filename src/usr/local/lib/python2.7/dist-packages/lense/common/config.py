import re
from os.path import isfile

# Lense Libraries
from lense import PKG_ROOT
from lense.common.vars import LENSE_CONFIG
from lense.common.objects import JSONObject
from lense.common.collection import Collection

class _LenseConfig(object):
    """
    Private class for constructing a configuration object.
    """
    def __init__(self, conf):
        
        # Configuration file
        self.conf = conf

        # JSON object manager
        self.json = JSONObject()

        # Configuration collection
        self.collection = self._build_config()
        
    def _build_config(self):
        """
        Internal method to build the configuration collection.
        """
        
        # Parse the default and user configuration files
        def_config = self.json.from_config_file(self.conf.replace('.json', '.default.json'))
        usr_config = {} if not isfile(self.conf) else self.json.from_config_file(self.conf)
        
        # Merge the configuration files
        for section, attrs in def_config.iteritems():
            if not section in usr_config:
                usr_config[section] = attrs
            else:
                for key, value in attrs.iteritems():
                    if not key in usr_config[section]:
                        usr_config[section][key] = value
    
        # Scan for substitution values
        for section, attrs in usr_config.iteritems():
            for key, value in attrs.iteritems():
                
                # If processing a relative path
                if isinstance(value, str) and re.match(r'^[^\/][\/]+', value):
                    usr_config[section][key] = '{}/{}'.format(PKG_ROOT, value)
    
        # Parse the configuration file
        return Collection(usr_config).get()
    
def parse(config_id=None):
    """
    Parse a configuration file based on a file ID. For a list of supported
    IDs, please look at the 'CONFIG' collection defined in 'lense.common.vars'
    """
    
    # Make sure the ID is valid
    if hasattr(LENSE_CONFIG, config_id):
        return _LenseConfig(getattr(LENSE_CONFIG, config_id)).collection
    
    # Invalid configuration ID
    raise Exception('Invalid configuration ID: {}'.format(config_id))