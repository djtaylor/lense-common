from sys import argv
from copy import copy
from json import dumps
from argparse import ArgumentParser, RawTextHelpFormatter

class BootstrapArgs(object):
    """
    Class object for handling arguments passed to the bootstrap manager.
    """
    def __init__(self):
        
        # Arguments parser / object
        self.parser  = None
        self._args   = None
        
        # Construct arguments
        self._construct()
        
    def list(self):
        """
        Return a list of argument keys.
        """
        return self._args.keys()
        
    def _return_help(self):
         return ("Lense Bootstrap Manager\n\n"
                 "A utility designed to handle bootstrapping a Lense installation. The\n"
                 "default action is to bootstrap all projects unless otherwise specified\n"
                 "with arguments.")
        
    def _construct(self):
        """
        Construct the argument parser.
        """
        
        # Create a new argument parsing object and populate the arguments
        self.parser = ArgumentParser(description=self._return_help(), formatter_class=RawTextHelpFormatter)
        self.parser.add_argument('-e', '--engine', help='Bootstrap the Lense API engine', action='store_true')
        self.parser.add_argument('-p', '--portal', help='Bootstrap the Lense API portal', action='store_true')
        self.parser.add_argument('-c', '--client', help='Bootstrap the Lense API client', action='store_true')
        self.parser.add_argument('-s', '--socket', help='Bootstrap the Lense API Socket.IO proxy', action='store_true')
        self.parser.add_argument('-d', '--dbinit', help='Set database intialization environment variables from a file', action='append')
        self.parser.add_argument('-a', '--answers', help='Path to an optional answers file to speed up bootstrapping', action='append')
      
        # Parse CLI arguments
        _argv = copy(argv)
        _argv.pop(0)
        self._args = vars(self.parser.parse_args(_argv))
        
    def set(self, k, v):
        """
        Set a new argument or change the value.
        """
        self._args[k] = v
        
    def get(self, k, default=None, use_json=False):
        """
        Retrieve an argument passed via the command line.
        """
        
        # Get the value from argparse
        _raw = self._args.get(k)
        _val = (_raw if _raw else default) if not isinstance(_raw, list) else (_raw[0] if _raw[0] else default)
        
        # Return the value
        return _val if not use_json else dumps(_val)