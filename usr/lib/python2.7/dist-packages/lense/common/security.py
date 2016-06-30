import struct
import random
import hashlib
from os.path import isfile, getsize
from Crypto.Cipher import AES

# Lense Libraries
from lense.common.exceptions import SecurityError

class LenseFileSecurity(object):
    """
    Manage security for files.
    """
    chunk_size = 64*1024
    
    @classmethod
    def checksum(cls, filename):
        """
        Calculate a checksum for a local file.
        """
        if not isfile(filename):
            raise SecurityError('Cannot calculate checksum for {0}: file not found'.format(filename))
        
        # Find the hash of the file
        hash_obj = hashlib.sha256(open(filename, 'rb').read())
        return hash_obj.hexdigest()

    @classmethod
    def encrypt(cls, infile, outfile, key):
        """
        Encrypt a file using PyCrypto and an encryption key.
        """
        
        # Input file must exist
        if not isfile(infile):
            raise SecurityError('Cannot encrypt {0}: file not found'.format(infile))
        
        # Output file path must be available
        if isfile(outfile):
            raise SecurityError('Cannot encrypt {0}: output file already exists'.format(outfile))
        
        # Encrypt the file
        iv        = b''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        filesize  = getsize(infile)
        with open(infile, 'rb') as ifh:
            with open(outfile, 'wb') as ofh:
                ofh.write(struct.pack('<Q', filesize))
                ofh.write(iv)
                while True:
                    chunk = ifh.read(cls.chunk_size)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += b' ' * (16 - len(chunk) % 16)
                    ofh.write(encryptor.encrypt(chunk))
        return True
    
    @classmethod
    def decrypt(cls, infile, outfile, key):
        """
        Decrypt a file using PyCrypto and an encryption key.
        """
        
        # Input file must exist
        if not isfile(infile):
            raise SecurityError('Cannot decrypt {0}: file not found'.format(infile))
        
        # Output file path must be available
        if isfile(outfile):
            raise SecurityError('Cannot decrypt {0}: output file already exists'.format(outfile))
        
        # Decrypt the file
        with open(infile, 'rb') as ifh:
            origsize  = struct.unpack('<Q', ifh.read(struct.calcsize('Q')))[0]
            iv        = ifh.read(16)
            decryptor = AES.new(key, AES.MODE_CBC, iv)
            with open(outfile, 'wb') as ofh:
                while True:
                    chunk = ifh.read(cls.chunk_size)
                    if len(chunk) == 0:
                        break
                    ofh.write(decryptor.decrypt(chunk))
                ofh.truncate(origsize)
        return True

class LenseSecurity(object):
    """
    Class wrapper for built in security functions.
    """
    def __init__(self):
        self.FILE = LenseFileSecurity