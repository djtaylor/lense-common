#!/usr/bin/python
from setuptools import setup, find_packages

# Import the module version
from lense.common import __version__

# Run the setup
setup(
    name             = 'lense-common',
    version          = __version__,
    description      = 'Common Python libraries for the Lense API engine',
    long_description = open('DESCRIPTION.rst').read(),
    author           = 'David Taylor',
    author_email     = 'djtaylor13@gmail.com',
    url              = 'http://github.com/djtaylor/lense-common',
    license          = 'GPLv3',
    install_requires = ['pycrypto>=2.6.1'],
    packages         = find_packages(),
    keywords         = 'lense module library common',
    classifiers      = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Terminals',
    ]
)