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
        def_config = self.json.from_config_file(re.compile(r'\.conf').sub('.default.conf', self.conf))
        usr_config = {} if not isfile(self.conf) else json.from_config_file(self.conf)
        
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
                if re.match(r'^[^\/][\/]+', value):
                    
    
        # Parse the configuration file
        self.collection = Collection(usr_config).get()

def _construct(config_file):
    """
    Parse and return a colletion from a JSON configuration file.
    """
    
    # JSON object manager
    json = JSONObject()

    # Parse the default and user configuration files
    def_config = json.from_config_file(re.compile(r'\.conf').sub('.default.conf', config_file))
    usr_config = {} if not isfile(config_file) else json.from_config_file(config_file)

    

def parse(config_id=None):
    """
    Parse a configuration file based on a file ID. For a list of supported
    IDs, please look at the 'CONFIG' collection defined in 'lense.common.vars'
    """
    
    # Make sure the ID is valid
    if hasattr(LENSE_CONFIG, config_id):
        return _LenseConfig(getattr(LENSE_CONFIG, config_id)).collection
        
        return _construct()
    
    # Invalid configuration ID
    raise Exception('Invalid configuration ID: {}'.format(config_id))