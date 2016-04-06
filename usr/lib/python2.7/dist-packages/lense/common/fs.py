from shutil import rmtree
from shutil import move as move_file
from os import makedirs, symlink, unlink
from os.path import isfile, islink, isdir

class LenseFS(object):
    """
    Filesystem utilities.
    """
    @classmethod
    def rmfile(cls, file):
        """
        Remove a file/symlink if it exists.
        
        :param file: The target file
        :type  file: str
        """
        if isfile(file) or islink(file):
            unlink(file)
    
    @classmethod    
    def rmdir(cls, path):
        """
        Recursively remove a directory.
        
        :param path: The directory to remove
        :type  path: str
        """
        if isdir(path):
            rmtree(path)
        
    @classmethod
    def mvfile(cls, src, dst):
        """
        Move a file from one place to another.
        
        :param src: The source file
        :type  src: str
        :param dst: The destination file
        :type  dst: str
        """
        move_file(src, dst)
        
    @classmethod
    def mklink(cls, target, link):
        """
        Make a symbolic link.
        
        :param target: The target file
        :type  target: str
        :param   link: The target link
        :type    link: str
        """
        symlink(target, link)
        
    @classmethod
    def mkdir(cls, dir_path):
        """
        Make a directory and return the path name.
        
        :rtype: str
        """
        if not isdir(dir_path):
            makedirs(dir_path)
        return dir_path