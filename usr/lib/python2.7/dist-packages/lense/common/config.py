import re
from os.path import isfile
from json import dumps as dump_json

# Lense Libraries
from lense.common.vars import CONFIG
from lense.common.objects import JSONObject
from lense.common.collection import Collection

class LenseConfigEditor(object):
    """
    Public class for editing an existing JSON configuration file.
    """
    def __init__(self, config_id):
        if not hasattr(LENSE_CONFIG, config_id):
            raise Exception('Invalid configuration ID: {0}'.format(config_id))

        # Open the configuration object
        self.json = JSONObject()
        self.file = getattr(CONFIG, config_id)
        self.conf = self.json.from_config_file(self.file)

    def set(self, path, value):
        """
        Set a new value.
        """
        
        # Store the configuration
        _obj   = self.conf
        
        # Path keys / length
        _paths = path.split('/')
        _len   = len(_paths)
        _count = 1
        
        # Set the new value
        for k in _paths:
            if _count == _len:
                _obj[k] = value
            else:
                _obj = _obj[k]
            _count += 1

    def save(self):
        """
        Save out the updated configuration.
        """
        with open(self.file, 'w') as f:
            f.write(dump_json(self.conf, indent=4))

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
                if not isinstance(attrs, dict):
                    usr_config[section] = attrs
                else:
                    for key, value in attrs.iteritems():
                        if not key in usr_config[section]:
                            usr_config[section][key] = value
    
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
    raise Exception('Invalid configuration ID: {0}'.format(config_id))