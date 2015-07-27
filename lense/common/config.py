import re
from os.path import isfile

# Lense Libraries
from lense import PKG_ROOT
from lense.common.vars import LENSE_CONFIG, LOG_DIR, PID_DIR
from lense.common.objects import JSONObject
from lense.common.collection import Collection

# Substitution values
SUB_VALUES = {
    'PKG_ROOT': PKG_ROOT,
    'LOG_DIR':  LOG_DIR,
    'PID_DIR':  PID_DIR
}

def _construct(config_file):
    """
    Parse and return a colletion from a JSON configuration file.
    """
    
    # JSON object manager
    json = JSONObject()

    # Parse the default and user configuration files
    def_config = json.from_config_file(re.compile(r'\.conf').sub('.default.conf', config_file))
    usr_config = {} if not isfile(config_file) else json.from_config_file(config_file)

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
            for sub_key, sub_val in SUB_VALUES.iteritems():
                if re.compile(r'^.*\{{}\}.*$'.format(sub_key)).match(value):
                    usr_config[section][key] = re.compile(r'(^.*)\{{}\}(.*$)'.format(sub_key)).sub(r'\g<1>{}\g<2>'.format(sub_val), value)

    # Parse the configuration file
    return Collection(usr_config).get()

def parse(config_id=None):
    """
    Parse a configuration file based on a file ID. For a list of supported
    IDs, please look at the 'CONFIG' collection defined in 'lense.common.vars'
    """
    
    # Make sure the ID is valid
    if hasattr(LENSE_CONFIG, config_id):
        return _construct(getattr(LENSE_CONFIG, config_id))
    
    # Invalid configuration ID
    raise Exception('Invalid configuration ID: {}'.format(config_id))