import os
import gzip
import zipfile
from tarfile import TarFile, TarError

"""
Extractor Helper Method

Class to allow the extraction of differen types of archive files
regardless of type.
"""
def unpack(file=None, base=None):
    if not file or not os.path.isfile(file):
        return False
    
    # Read the file into a StringIO object
    file_obj = open(file, 'r')
    
    # File type marker
    file_type = False
    
    # Check if the file is a tarball
    try:
        tar_file = TarFile(fileobj=file_obj)
        file_type = 'tar'
    except TarError:
        pass
    
    # Check if the file is a zip file
    if not file_type:
        if zipfile.is_zipfile(file):
            file_type = 'zip'
            
    # Check if the file is gzip compressed
    if not file_type:
        if gzip.GzipFile(file):
            file_type = 'gzip'
            
    # If the file type was not found
    if not file_type:
        return False
    
    # Unpack the file
    if file_type == 'tar':
        if base and os.path.isdir(base):
            os.system('tar xzf %s -C %s' % (file, base))
        else:
            os.system('tar xzf %s' % file)
    if file_type == 'zip':
        if base and os.path.isdir(base):
            os.system('unzip %s -d %s' % (file, base))
        else:
            os.system('unzip %s' % file)
    if file_type == 'gzip':
        if base and os.path.isdir(base):
            os.system('tar xzf %s -C %s' % (file, base))
        else:
            os.system('tar xzf %s' % file)
    return True