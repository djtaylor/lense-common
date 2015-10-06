import os
import re
import shutil

class CParse(object):
    """
    Helper class designed to parse and set options in configuration files. Should
    be able to handle different configuration formats, such as:
    
    directive = value
    directive value
    flag
    """
    def __init__(self):
        
        # Target configuration file and parsed contents
        self.target_file = None
        self.target_conf = []
        self.target_attr = {}
        self.target_out  = ''
        
        # Target backup
        self.target_bak  = None
        
        # File is INI style
        self.is_ini      = False
        
    def _backup(self):
        """
        Create a backup of the config file.
        """
        try:
            shutil.copyfile(self.target_file, self.target_bak)
        except Exception as e:
            raise Exception('Failed to backup file [{}]: {}'.format(self.target_file, str(e)))
        
    def _restore(self):
        """
        Restore the original file.
        """
        try:
            shutil.copyfile(self.target_bak, self.target_file)
            os.unlink(self.target_bak)
        except Exception as e:
            raise Exception('Failed to restore backup file [{}]: {}'.format(self.target_bak, str(e)))
        
    def _reset(self):
        """
        Reset the configuration objects if using the same instance to select another
        config file.
        """
        self.target_file = None
        self.target_conf = []
        self.target_attr = {}
        self.target_out  = ''
        self.is_ini      = False
        
    def select(self, file):
        """
        Select the target configuration file to parse. Load the raw file contents
        into a list, then extract configuration directives and sections if targeting
        an INI style object.
        
        :param file: The target config file
        :type file: str
        """
        if not os.path.isfile(file):
            raise Exception('Target file [{}] does not exist'.format(file))
        
        # Reset if already instantiated
        self._reset()
        
        # Set the target file
        self.target_bak  = '{}.bak'.format(file)
        self.target_file = file
        
        # Read the file into memory
        with open(self.target_file, 'r') as f:
            section = None
            for l in f.readlines():
                self.target_conf.append(l.rstrip())
                
                # Extract directives
                if l.strip():
                    
                    # If parsing an INI style file
                    if l.startswith('['):
                        self.is_ini = True
                        section = re.compile(r'^\[([^\]]*)\]$').sub(r'\g<1>', l.rstrip())
                        self.target_attr[section] = {}
                        continue
                    
                    if not l.startswith('#'):
                        
                        # If parsing a key/pair value
                        if (' ' in l) or ('=' in l):
                            
                            # If using a directive seperator
                            if '=' in l:
                                e = re.compile(r'(^[^=\s]*)\s*=\s*(.*$)')
                                k = e.sub(r'\g<1>', l.rstrip())
                                v = e.sub(r'\g<2>', l.rstrip())
                                ds = '='
                                
                            # If directive/value seperated by a space
                            else:
                                e = re.compile(r'(^[^\s]*)\s+(.*$)')
                                k = e.sub(r'\g<1>', l.rstrip())
                                v = e.sub(r'\g<2>', l.rstrip())
                                ds = ' '
                            
                            # Set the configuration attribute
                            if section:
                                self.target_attr[section][k] = [ds, v]
                            else:
                                self.target_attr[k] = [ds, v]
                            
                        # If parsing a configuration flag
                        else:
                            if section:
                                self.target_attr[section][l.rstrip()] = None
                            else:
                                self.target_attr[l.rstrip()] = None
        return True
    
    def del_section(self, s):
        """
        Remove a section from an INI file.
        
        :param s: Section name
        :type s: str
        """
        if not self.is_ini:
            return False
        if not s in self.target_attr:
            return True
        del self.target_attr[s]
        return True
    
    def add_section(self, s):
        """
        Add a new section to an INI file.
        
        :param s: Section name
        :type s: str
        """
        if not self.is_ini:
            return False
        if s in self.target_attr:
            return True
        self.target_attr[s] = {}
        return True
    
    def del_key(self, k, s=None):
        """
        Delete a key from the existing configuration object.
        
        :param k: The target key to delete
        :type k: str
        """
        if self.is_ini:
            if s:
                if not s in self.target_attr:
                    raise Exception('Configuration section [{}] does not exist'.format(s))
                if k in self.target_attr[s]:
                    del self.target_attr[s][k]
                return True
            else:
                for _k, _v in self.target_attr.iteritems():
                    if k in _v:
                        del _v[k]
                return True
        else:
            if k in self.target_attr:
                del self.target_attr[k]
            return True
    
    def get_key(self, k, s=None):
        """
        Retrieve a key value from the parsed configuration object.
        
        :param k: The target key
        :type k: str
        :param s: The section if parsing an INI file
        :type s: str
        :rtype: str|boolean
        """
        if self.is_ini:
            if s:
                if s in self.target_attr:
                    if k in self.target_attr[s]:
                        return self.target_attr[s][k]
                    return False
                return False
            else:
                for _k, _v in self.target_attr:
                    if k in _v:
                        return _v[k]
                return False
        else:
            if k in self.target_attr:
                return self.target_attr[k]
            return False
            
    def set_key(self, k, v, d='=', s=None):
        """
        Set a new key or update an exiting key in the configuration object. If
        targeting an INI style object, and the key does not exist yet, you must
        specify a section or else an exception will be raised. If you want a 
        directive seperator different from the default '=', you must override the
        'd' argument.
        
        :param k: The configuration key
        :type k: str
        :param v: The configuration value
        :type v: str
        :param d: The directive seperator
        :type d: str
        :param s: The INI section
        :type s: str
        """
        if self.is_ini:
            keyset = False
            for _section, _pairs in self.target_attr.iteritems():
                if s == _section:
                    if k in _pairs:
                        _pairs[k] = [d, v]
                        keyset = True
                        break
            if not keyset:
                if not s:
                    raise Exception('Key [{}] not found, must specify a section to insert new parameter into an INI file'.format(k))
                else:
                    if not s in self.target_attr:
                        raise Exception('Section [{}] not found, must add first using \'add_section("section")\''.format(s))
                    self.target_attr[s][k] = [d, v]
                    return True
            return True
        else:
            self.target_attr[k] = [d, v]
            return True
       
    def _write_config(self):
        """
        Write out the recontructed configuration object.
        """
        try:
            fh = open(self.target_file, 'w')
            fh.write(self.target_out)
            fh.close()
            return True
        except Exception as e:
            self._restore()
            os.unlink(self.target_bak)
            raise Exception('Failed to write out configuration: {}'.format(str(e)))
            
    def apply(self):
        """
        Reconstruct the config file and re-apply after making changes.
        """
        if self.is_ini:
            count = 0
            for k,v in self.target_attr.iteritems():
                pre = '\n' if not (count == 0) else ''
                self.target_out += '{}[{}]\n'.format(pre, k)
                for _k, _v in v.iteritems():
                    if not _v:
                        self.target_out += '{}\n'.format(_k)
                    else:
                        self.target_out += '{}{}{}\n'.format(_k, _v[0], _v[1])
                count += 1
        else:
            for k,v in self.target_attr.iteritems():
                if not v:
                    self.target_out += '{}\n'.format(k)
                else:
                    self.target_out += '{}{}{}\n'.format(_k, _v[0], _v[1])
        
        # Backup the file
        self._backup()
        
        # Write out the configuration
        self._write_config()
        
        # Clear the backup
        os.unlink(self.target_bak)