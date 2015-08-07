#!/usr/bin/python
from sys import path
from setuptools import setup, find_packages

# Add the local path
path.append('usr/local/lib/python2.7/dist-packages')

# Import the module version
from lense.common import __version__

# Module version / long description
version   = __version__
long_desc = open('DESCRIPTION.rst').read()

# Run the setup
setup(
    name             = 'lense-common',
    version          = version,
    description      = 'Lense API engine common libraries',
    long_description = long_desc,
    author           = 'David Taylor',
    author_email     = 'djtaylor13@gmail.com',
    url              = 'http://github.com/djtaylor/lense-common',
    license          = 'GPLv3',
    package_dir      = {'': 'src/usr/local/lib/python2.7/dist-packages'},
    packages         = find_packages(),
    keywords         = 'lense common libraries engine api'
    classifiers      = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)