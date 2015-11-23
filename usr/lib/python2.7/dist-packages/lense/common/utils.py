from __future__ import print_function
import re
import os
import sys
import json
import uuid
import struct
import string
import random
import hashlib
import operator
import importlib
import subprocess
from os import geteuid
from Crypto.Cipher import AES

# Lense Libraries
from lense.common import config
from lense.common import logger
from lense.common.vars import CONFIG

def ensure_root():
    """
    Make sure the current process is being run as root or with sudo privileges.
    """
    if not geteuid() == 0:
        print('ERROR: This script must be run as root or with sudo privileges')
        sys.exit(1)

def set_response(rsp_obj, default):
    """
    Convenience method for returning a default value if the queried utility has no return values.
    """
    return default if not rsp_obj else rsp_obj

def truncate(string, length=75):
    """
    Return a truncated string.
    """
    return (string[:75] + '...') if len(string) > 75 else string

def rstring(length=12):
    """
    Helper method used to generate a random string.
    """
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(length)])

def autoquote(v):
    """
    Autoquote a return value. If the value is a string, quote and return. If the
    object is a type of number, do not quote. If the object is boolean or an
    object, return a representation.
    """
    
    # Int / Float / Long / Complex
    if (isinstance(v, int)) or (isinstance(v, float)) or (isinstance(v, long)) or (isinstance(v, complex)):
        return v
    
    # True / False / None / List / Dictionary
    elif (v == None) or (v == False) or (v == True) or (isinstance(v, list)) or (isinstance(v, dict)):
        return repr(v)
    
    # String / Unicode / etc.
    else:
        return '[%s]' % v

def mod_has_class(mod, cls, no_launch=False):
    """
    Helper method used to check if a module file contains a class definition.
    
    :param mod: The path to the module to inspect
    :type mod: str
    :param cls: The class definition name
    :type cls: str
    """

    # Try to import the module
    try:
        mod_inst = importlib.import_module(mod)
        
        # Make sure the module has the class definition
        if not hasattr(mod_inst, cls):
            return invalid('Class definition <{0}> not found in module <{1}>'.format(cls, mod))
        
        # Create an instance of the class
        cls_inst = getattr(mod_inst, cls)
        if not no_launch:
            if not hasattr(cls_inst, 'launch') or not callable(cls_inst.launch):
                return invalid('Class <{0}.{1}> requires a callable <launch> method definition'.format(mod, cls))
        return valid()
    except Exception as e:
        return invalid('Failed to import module <{0}>: {1}'.format(mod, str(e)))

def obj_extract(obj, id=None, filter=None, auto_quote=True):
    """
    Helper method used to extract details from a JSON object structure
    depending on a root ID (optional) and a filter.
    
    :param obj: The JSON object to extract from
    :type obj: list|dict
    :param id: The optional root ID if using a multi key object
    :type id: str
    :param filter: The object filter as parsed by this method
    :type filter:
    :rtype: str
    """
    if not id and not filter:
        return obj
    
    # Get the base object
    base_obj = obj if not id else obj[id]
    
    # If no filter specified
    if not filter:
        return obj if not (id in obj) else obj[id]
    
    # Break up the filter
    fv = filter.split('.')
    
    # Extract the data
    def _inner(_obj, _fv):
        if isinstance(_obj, list):
            for o in _obj:
                if re.match(r'^\[.*\]$', _fv[0]):
                    lv = re.compile(r'^\[(.*)\]$').sub(r'\g<1>', _fv[0])
                    for k,v in o.iteritems():
                        if lv == v:
                            _fv.pop(0)
                            if _fv[0] in o:
                                return _inner(o, _fv)
                if _fv[0] in o:
                    _fv.pop(0)
                    return _inner(o, _fv)
        if isinstance(_obj, dict):
            for k,v in _obj.iteritems():
                if len(_fv) == 1:
                    if k == _fv[0]:
                        return v if not auto_quote else autoquote(v)
                else:
                    if k == _fv[0]:
                        _fv.pop(0)
                        return _inner(v, _fv)
    return _inner(base_obj, fv)

def valid(msg=None, data=None, code=200):
    """
    Return valid request object. Used internally by the API to pass data between methods.
    Contains a boolean 'valid' flag as well as the data to return to the calling method.
    
    Example usage::
    
        # Import the utilities
        from lense.common.utils import valid, invalid
    
        # Some external class
        from awesome.module import Constructor
    
        # Some internal class
        class APIClass:
        
            # Some internal method
            def _im_internal(self):
                
                # Constructing an object
                try:
                    construct_me = Constructor()
                    
                    # Everything OK
                    return valid(construct_me)
                    
                # FAIL!
                except Exception as e:
                    return invalid(str(e)
                    
            # Some public method
            def im_public(self):
            
                # Call the internal method
                status = self._im_internal()
                
                # If the response is valid
                if not status['valid']:
                
                    # Return the error message. Any API objects calling this should know
                    # how to handle the dictionary response. Ultimately this gets passed
                    # back to the API request handler.
                    return status
                    
                # Get the constructed object
                some_obj = status['content']
                
    :param msg: An optional message or return content
    :type msg: str|list|dict|class|method
    :param data: Additional data that can be returned to the API client
    :type data: dict|list|str
    :rtype: dict
    """
    if not msg:
        return { 'valid': True, 'content': None , 'data': data, 'code': code }
    return { 'valid': True, 'content': msg , 'data': data , 'code': code }

def invalid(msg, code=400):
    """
    Similar to the 'valid' method in usage. Returns a dictionary with the 'valid' flag
    set to false. Can specify an optional HTTP return code. Takes an error message or 
    object as the first argument.
    
    :param msg: The error message or object
    :type msg: str|list|dict
    :param code: The HTTP response code, defaults to 400
    :type code: int
    :rtype: dict
    """
    return { 'valid': False, 'code': code, 'content': msg }

def format_action(a, m, w=10, b=False):
    """
    Simple helper method used to format action entries in the help prompt for the Cloudscape
    agent.
    
    :param a: The action string
    :type a: str
    :param m: The action help message
    :type m: str
    :param w: The width of the action column
    :type w: int
    :param b: Use a carriage return in the output
    :type b: boolean
    :rtype: str
    """
    b = '' if not b else '\r'
    return "{0:<{1}}{2}{3}\n".format(a, w, m, b)

class UtilsBase(object):
    """
    Utilities base class for specific classes. Constucts the configuration and logging
    objects depending if you are on a server or agent.
    """
    def __init__(self, child):
        """
        Class constructor.
        
        :param child: Child class object
        :type child: class object
        """
    
        # Define the logger name
        log_name  = '{}.{}'.format(__name__, child.__class__.__name__)

        # Running utilities on the server
        if os.path.isfile(CONFIG.ENGINE):
            self.conf = config.parse('ENGINE')
            self.log  = logger.create(log_name, self.conf.utils.log)
            
        # Raise an exception if neither the server nor agent configuration is found
        else:
            raise Exception('Could not locate the server configuration')

class FileSec(UtilsBase):
    """
    File security class. Used to generate checksums, as well as encrypt and 
    decrypt files.
    """
    def __init__(self):
        super(FileSec, self).__init__(self)
        
        # File chunk size
        self.chunk_size = 64*1024
    
    def checksum(self, filename=None):
        """
        Generate and return a SHA256 checksum of a target file.
        
        Get a file checksum::
        
            # Import the utility and create an instance
            from lense.common.utils import FileSec
            fs = FileSec()
            
            # Get the checksum of a file
            csum = fs.checksum('/path/to/file.txt')
        
        :param filename: The file name to checksum
        :type filename: str
        :rtype: str
        """
        if not filename or not os.path.isfile(filename):
            return False
        
        # Find the hash of the file
        hash_obj = hashlib.sha256(open(filename, 'rb').read())
        checksum = hash_obj.hexdigest()
        
        # Log and return the checksum
        self.log.info('Generating SHA256 checksum [{}] for: {}'.format(checksum, filename))
        return checksum
    
    def encrypt(self, infile, outfile, key):
        """
        Encrypt a file using PyCrypto and an encryption key.
        
        Encrypt a file::
        
            # Import the utility and create an instance
            from lense.common.utils import FileSec
            fs = FileSec()
            
            # Input and output file
            infile = '/some/file.txt'
            outfile = '/some/file.txt.enc'
            
            # Encryption key
            key = 'secret'
            
            # Encrypt a file
            fs.encrypt(infile, outfile, key)
        
        :param infile: The file to encrypt
        :type infile: str
        :param outfile: The encrypted file path
        :type outfile: str
        :param key: The encryption key
        :type key: str
        :rtype: boolean
        """
        if not os.path.isfile(infile):
            self.log.error('Failed to enrypt file [{}]: file not found'.format(infile))
            return False 
        if os.path.isfile(outfile):
            self.log.error('Failed to encrypt file - output file [{}] already exists'.format(outfile))
            return False
        
        # Encrypt the file
        iv        = b''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        filesize  = os.path.getsize(infile)
        with open(infile, 'rb') as ifh:
            with open(outfile, 'wb') as ofh:
                ofh.write(struct.pack('<Q', filesize))
                ofh.write(iv)
                while True:
                    chunk = ifh.read(self.chunk_size)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += b' ' * (16 - len(chunk) % 16)
                    ofh.write(encryptor.encrypt(chunk))
        self.log.info('Encrypting file [{}] to [{}] using AES-256 and key string'.format(infile, outfile))
        return True
    
    def decrypt(self, infile, outfile, key):
        """
        Decrypt a file using PyCrypto and an encryption key.
        
        Decrypt a file::
        
            # Import the utility and create an instance
            from lense.common.utils import FileSec
            fs = FileSec()
            
            # Input and output file
            infile = '/some/file.txt.enc'
            outfile = '/some/file.txt'
            
            # Encryption key
            key = 'secret'
            
            # Decrypt a file
            fs.decrypt(infile, outfile, key)
        
        :param infile: The file to decrypt
        :type infile: str
        :param outfile: The decrypted file path
        :type outfile: str
        :param key: The encryption key
        :type key: str
        :rtype: boolean
        """
        if not os.path.isfile(infile):
            self.log.error('Failed to decrypt file [{}]: file not found'.format(infile))
            return False 
        if os.path.isfile(outfile):
            self.log.error('Failed to decrypt file - output file [{}] already exists'.format(outfile))
            return False
        
        # Decrypt the file
        with open(infile, 'rb') as ifh:
            origsize  = struct.unpack('<Q', ifh.read(struct.calcsize('Q')))[0]
            iv        = ifh.read(16)
            decryptor = AES.new(key, AES.MODE_CBC, iv)
            with open(outfile, 'wb') as ofh:
                while True:
                    chunk = ifh.read(self.chunk_size)
                    if len(chunk) == 0:
                        break
                    ofh.write(decryptor.decrypt(chunk))
                ofh.truncate(origsize)
        self.log.info('Decrypting file [{}] to [{}] using AES-256 and key string'.format(infile, outfile))
        return True

class JSONTemplate(UtilsBase):
    """
    A utility class designed to validate a JSON object against a template file. Used
    to verify the structure of API requests.
    """
    def __init__(self, template=None):
        super(JSONTemplate, self).__init__(self)
        
        # Set the template object
        self.template_obj = template

        # Template and target file objects
        self.template     = None
        self.target       = None

    def _is_type(self, var, type):
        """
        Helper method used to simplify testing for differen types of variables, as well
        as validating non-builtin Python types, such as UUID4, IPv4, etc.
        
        :param var: The variable to test
        :type var: str|list|dict|int|bool
        :param type: The type the variable should be
        :type type: str
        :rtype: boolean
        """
        if type == 'dict':
            if isinstance(var, dict):
                return True
            return False
        if type == 'list':
            if isinstance(var, list):
                return True
            return False
        if type == 'str':
            if isinstance(var, (str, unicode, basestring)):
                return True
            return False
        if type == 'int':
            if isinstance(var, (int, float, long)):
                return True
            return False
        if type == 'uuid4':
            try:
                v = uuid.UUID(var, version=4)
                return True
            except:
                return False
        if type == 'bool':
            if isinstance(var, bool):
                return True
            return False
        if type == '*':
            return True
    
    def _load_json(self, json_obj):
        """
        Helper method to load and validate basic JSON structure to see if it is
        syntactically correct.
        
        :param obj: The JSON object to validate
        :type obj: dict|list
        :rtype: valid|invalid
        """
        
        # If the object is a string type
        if self._is_type(json_obj, 'str'):
            try:
                return valid(json.loads(json_obj))
            except Exception as e:
                return invalid('Target object is not valid JSON: {}'.format(str(e)))
            
        # If the object is a list or dictionary
        if isinstance(json_obj, (dict, list)):
            try:
                obj_tmp = json.dumps(json_obj)
            except:
                return invalid('Target object is not valid JSON: {}'.format(str(e)))
            return valid(json_obj)
            
        # JSON object must be a string or list/dictionary
        return invalid('Target object must be either a string or a list/dictionary')
    
    def _parse_json(self, target_obj):
        """
        Parse the JSON validation template and target object.
        """
        
        # If either of the objects are not valid
        template_obj = self._load_json(self.template_obj)
        target_obj   = self._load_json(target_obj)
        
        # Make sure the template object is valid
        if not template_obj['valid']:
            return template_obj['content']
        
        # Make sure the target object is valid
        if not target_obj['valid']:
            return target_obj['content']
        
        # Load the validation objects
        self.template = template_obj['content']
        self.target   = target_obj['content']
    
    def _path_error(self, map, msg):
        """
        Construct and return a JSON path error, showing exactly where validation failed and why.
        """
        return self.log.error('Error at {}: {}'.format(map, msg))
    
    def validate(self, target_str=None):
        """
        Validate a JSON object against a supplied template.
        """
        
        # Parse the JSON validation template and target object
        parse_err = self._parse_json(target_str)
        if parse_err:
            return parse_err

        # Set the parent object
        m = 'root'
        
        # Walk through a ditionary block
        # p:  Parent key
        # t:  Relative template block
        # f:  Relative formula block
        # m:  Current formula map
        # cb: Optional callblack function
        def _dict_walk(p,t,f,m,cb=None):
            
            # Walk through a list block
            # k: List block key
            # l: List object to walk through
            # t: Relative template object
            # m: Current formula map
            def _list_walk(k,l,t,m):
                c = 0
                for o in l:
                    
                    # If the list object is empty
                    if not o:
                        return self._path_error(m, 'List object is empty')
                    
                    # Validate the list object type
                    ot = t['_type']
                    if not self._is_type(o,ot):
                        return self._path_error(m, 'Invalid list object type')
                    
                    # Set the formula map
                    m += '/%d' % c if (c == 0) else re.compile('(^.*\/{}\/)[0-9]*(.*$)'.format(k)).sub(r'\g<1>{}\g<2>'.format(c), m)
                    
                    # Walk through nested items in the list
                    obj_err = _dict_walk(c,t,o,m)
                    if obj_err:
                        return obj_err
                    c += 1
            
            # Data type
            dt = t['_type']
            
            # Validate the data type of the current formula level
            if not self._is_type(f, dt):
                if ('_empty' in t) and (t['_empty'] == True):
                    pass
                else:
                    return self._path_error(m, 'Object is an invalid type, should be {}'.format(dt))
            
            # If the current level has no children
            if not '_children' in t:
                
                # Look for the values flag
                if '_values' in t and self._is_type(t['_values'], 'list'):
                    if self._is_type(f, 'list'):
                        for fk in f:
                            if not fk in t['_values']:
                                return self._path_error(m, 'Object value [{}] is not in supported values list: [{}]'.format(fk, ', '.join(t['_values'])))
                    else:
                        if f not in t['_values']:
                            return self._path_error(m, 'Object value [{}] is not in supported values list: [{}]'.format(f, ', '.join(t['_values'])))
            
                # Look for the integer range flag
                if '_range' in t and self._is_type(f, 'str'):
                    b = re.compile('(^[^\/]*)\/[^\/]*$').sub(r'\g<1>', f)
                    e = re.compile('^[^\/]*\/([^\/]*$)').sub(r'\g<1>', f)
                    if not int(b) <= int(f) <= int(e):
                        return self._path_error(m, 'Object value [{}] must be between [{}] and [{}]'.format(f, b, e))
            
            # If the current level has children
            else:
                
                # Required and optional keys
                rk = t['_required']
                ok = t['_optional']
                
                # Make sure all required keys are set
                mkv = []
                rks = []
                for rkv in rk:
                    
                    # If processing a group of alternate key choices
                    if self._is_type(rkv, 'list'):
                        akf = False
                        for ak in rkv:
                            if ak in f:
                                akf = True
                                rks.append(ak)
                        if not akf:
                            mkv.append('({})'.format('/'.join(rkv)))
                        
                    # Make sure the key is set
                    else:
                        if not rkv in f:
                            mkv.append(rkv)
                        else:
                            rks.append(rkv)
                
                # If any required keys are missing
                if mkv:
                    return self._path_error(m, 'Missing required key values: {}'.format(', '.join(mkv)))
                
                # Process the formula level
                for k,v in f.iteritems():
                    m += '/%s' % k
                    
                    # Check if the key is required, optional, or unsupported
                    wc = False
                    if not k in rks:
                        if not k in ok:
                            if not '*' in ok:
                                return self._path_error(m, 'Using unsupported key [{}] without wildcard flag'.format(k))
                            
                            # Current key is a wildcard entry
                            else:
                                wc = True
                
                    # Set the next template object
                    try:
                        to = t['_children']['*'] if wc else t['_children'][k]
                    except:
                        continue
                    tt = to['_type']
                    
                    # If the current formula key contains a list
                    if tt == 'list' and '_contains' in to:
                        
                        # Walk through the list objects
                        tco  = to['_contains']
                        lerr = _list_walk(k,v,tco,m)
                        if lerr:
                            return lerr
                    
                    # If current formula level contains a dictionary
                    else:
                        
                        # Make sure the value is set and the data type is correct
                        if not v and not self._is_type(v,'int'):
                            if ('_empty' in to) and (to['_empty'] == True):
                                pass
                            else:
                                return self._path_error(m, 'Value for key [{}] is not defined or empty'.format(k))
                        if not self._is_type(v,tt):
                            if ('_empty' in to) and (to['_empty'] == True):
                                pass
                            else:
                                return self._path_error(m, 'Invalid data type for key [{}], expected [{}]'.format((k,tt)))
                         
                        # Walk through the next level of the formula
                        ferr = _dict_walk(p,to,f[k],m)
                        if ferr:
                            return ferr
                   
                    # Reset the formula map
                    m = p if (p == 'root') else re.compile('(^.*)\/[^>]*$').sub(r'\g<1>', m)
            
            # Run the callback function
            if cb: cb()
                   
        # Recursive callback
        self.log.info('Initializing template validation run')
        def rcb():
            self.log.info('Completed template validation run')
                   
        # Walk through and validate the formula structure with the template
        return _dict_walk('root', self.template['root'], self.target, m, rcb)