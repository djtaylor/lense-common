import os
import re
import sys
import json

# Lense Libraries
from lense import import_class, set_arg
from lense.common.exceptions import JSONException

class LenseAPIObjects(object):
    """
    API object manager.
    """
    def __init__(self):
        self.HANDLER = import_class('ObjectInterface', 'lense.common.objects.handler')
        self.ACL     = import_class('ObjectInterface', 'lense.common.objects.acl')
        self.USER    = import_class('ObjectInterface', 'lense.common.objects.user')
        self.GROUP   = import_class('ObjectInterface', 'lense.common.objects.group')

class JSONObject(object):
    """
    Class for loading and abstracting access to a JSON object.
    """
    def __init__(self):
        
        # Comment regex pattern
        self.regex_comment = re.compile(r'^//.*$') 
    
        # Internal JSON object
        self._json = None
    
    def _is_comment_or_empty(self, line):
        """
        Check if a line contains a comment string or is empty.
        """
        line_empty   = line.isspace()
        line_comment = self.regex_comment.match(line.rstrip().lstrip())
        return True if (line_empty or line_comment) else False
    
    def from_config_file(self, file):
        """
        Construct a new JSON object from a custom configuration JSON file
        with embedded comments.
        """
        if os.path.isfile(file):
            try:
                
                # Since I will be using Python style comments in JSON, strip them out before reading
                json_str = ''
                with open(file) as f:
                    for line in f.readlines():
                        if not self._is_comment_or_empty(line):
                            json_str = '{0}{1}'.format(json_str, line.rstrip().lstrip())
                
                # Read the file after cleaning any comments
                self._json = json.loads(json_str)
                return self._json
            
            # Error reading file
            except Exception, e:
                raise JSONException('Failed to read file "{0}": {1}'.format(file, str(e)))
                
        # File not found
        else:
            raise JSONException('File not found: {0}'.format(file))
    
    def from_file(self, file):
        """
        Construct a new JSON object from a file.
        """
        if os.path.isfile(file):
            try:
                
                # Read the file after cleaning any comments
                self._json = json.load(open(file))
                return self._json
            
            # Error reading file
            except Exception, e:
                raise JSONException('Failed to read file "{0}": {1}'.format(file, str(e)))
                
        # File not found
        else:
            raise JSONException('File not found: {0}'.format(file))
    
    def from_string(self, string):
        """
        Construct a new JSON object from a string.
        """
        try:
            self._json = json.loads(string)
            return self._json
        
        # Error reading string
        except Exception, e:
            raise JSONException('Failed to read string: {0}'.format(str(e)))
        
    def search(self, filter, delimiter='/', default=None):
        """
        Search through the JSON object for a value.
        """
        
        # Search filter must be a list or string
        if not (isinstance(filter, list) or isinstance(filter, str)):
            raise JSONException('Search parameter must be a list or string, not "{0}"'.format(type(filter)))
        
        # Construct the search path
        search_path = filter if (isinstance(filter, list)) else filter.split(delimiter)
        
        # List filter regex
        _list_regex = re.compile(r'^\[([^=]*)=["\']([^"\']*)["\']\]$')
        
        # Process the search path
        def _search(_path, _json):
            
            # Dictionary boolean / search key / search value
            _is_dict    = True if isinstance(_json, dict) else False
            _search_key = _path[0] if _is_dict else _list_regex.sub(r'\g<1>', _path[0])
            _search_val = None if _is_dict else _list_regex.sub(r'\g<2>', _path[0])
            
            # If searching a dictionary
            if _is_dict:
                if _search_key in _json:
                    
                    # On the last search key
                    if len(_path) == 1:
                        return _json[_search_key]
                    
                    # More search keys to go
                    else:
                        _path.pop(0)
                        return _search(_path, _json[_search_key])
                    
                # Search key not found
                else:
                    return default
        
            # Searching a list
            else:
                for o in _json:
                    
                    # Search key found
                    if (_search_key in o):
                        _path.pop(0)
                        return o if not _path else _search(_path, o)
                            
                    # No list match found
                    else:
                        continue
                    
                # Search key/value not found in list
                return default
        
        # Return any discovered values
        return _search(search_path, self._json)