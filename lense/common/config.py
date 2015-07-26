import os.path
import ConfigParser

# Lense Libraries
from lense.common.vars import S_CONF, S_CONF_DEF
from lense.common.collection import Collection

# Boolean string values
BOOL_STRINGS = {
    'true':  ['True', 'true', 'yes', 'Yes'],
    'false': ['False', 'false', 'no', 'No']
}

class ServerConfig(object):
    """
    Construct and return the server configuration file.
    """ 
    def _map_value(self, value):
        """
        Map a string value depending on the type.
        """
        
        # True value
        if value in BOOL_STRINGS['true']:
            return True
        
        # False value
        if value in BOOL_STRINGS['false']:
            return False
        
        # Integer value
        try:
            return int(value)
        except:
            pass
        
        # String value
        return value
    
    def _to_dict(self, config):
        """
        Map a configuration object to a dictionary.
        """
        
        # Declare the configuration dictionary
        config_dict = {}
        
        # Process each configuration section
        for section in config.sections():
            section_opts = config.options(section)
            
            # Make sure the section exists in the dictionary
            if not section in config_dict:
                config_dict[section] = {}
            
            # Map each section and option to the dictionary object
            for opt in section_opts:
                config_dict[section][opt] = self._map_value(config.get(section, opt))
    
        # Return the configuration dictionary
        return config_dict
                
    def _parse(self, file):
        """
        Parse a configuration file and return a dictionary object.
        """
        
        # Make sure the default configuration file exists
        if not os.path.isfile(file):
            raise Exception('Could not locate configuration file: %s' % file)
    
        # Create a new configuration parser
        config = ConfigParser.ConfigParser()
        
        # Parse the configuration file
        try:
            config.read(file)
            
        # Failed to parse the configuration file
        except Exception as e:
            raise Exception('Failed to parse configuration [%s]: %s' % (file, str(e)))
    
        # Return a configuration dictionary
        return self._to_dict(config)
    
    def construct(self):
        """
        Construct the configuration and return an immutable collection object.
        """

        # Load the default configuration if the user-defined configuration doesn't exist
        if not os.path.isfile(S_CONF):
            return Collection(self._parse(S_CONF_DEF)).get()

        # Parse the default and user configuration files
        def_config = self._parse(S_CONF_DEF)
        usr_config = self._parse(S_CONF)
        
        # Merge the default configuration into the user configuration
        for section, options in def_config.iteritems():
            if not section in usr_config:
                usr_config[section] = def_config[section]
            else:
                for key, value in options.iteritems():
                    if not (key in usr_config[section]):
                        usr_config[section][key] = value
    
        # Return a configuration collection
        return Collection(usr_config).get()

def _construct(config_file):
    """
    Worker method to construct the named tuple configuration object. Loads
    the configuration using ConfigParser, converts to a dictionary, the to
    a named tuple using the Collection class. Raises an exception if:
    
    1.) The configuration could not be located
    2.) Failed to read the configuration file using ConfigParser
    3.) Failed to parse configuration sections
    
    :rtype: Named tuple of configuration values
    """

    # Bool values
    bool_values = ['True', 'False']

    # If the config file does not exist
    if not os.path.isfile(config_file):
        raise Exception('Could not locate configuration file: %s' % (config_file))
    
    # Parse the configuration file
    config = ConfigParser.ConfigParser()
    try:
        config.read(config_file)
    except:
        raise Exception('Failed to parse configuration file: %s' % (config_file))

    # Build a list of configuration sections
    try:
        config_sections = config.sections()
    except:
        raise Exception('Failed to parse configuration sections in: %s' % (config_file))
        
    # Build a dictionary of configuration options
    config_collector = Collection()
    for section in config_sections:
        section_opts = config.options(section)
        
        # Map each section and option to the collection object
        for opt in section_opts:
            
            # If parsing a boolean value
            if config.get(section, opt) in bool_values:
                config_collector.map({section: {opt: config.getboolean(section, opt)}})
                
            # If parsing a string value
            else:
                config_collector.map({section: {opt: config.get(section, opt)}})
            
    # Return the collection object
    return config_collector.get()

def parse(file=None):
    """
    Parse the configuration file. Detects whether running on the
    server or agent by the presence of each respective file. If the
    server configuration is found, load that. Otherwise, load the
    agent configuration.
    """
    
    # If manually specifying a file
    if file:
        return _construct(file)
    return ServerConfig().construct()