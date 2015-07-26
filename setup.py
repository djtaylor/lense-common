#!/usr/bin/python
import lense.common as lense_common
from setuptools import setup, find_packages

# Module version / long description
version = lense_common.__version__
long_desc = open('DESCRIPTION.rst').read()

# Run the setup
setup(
    name='lense-common',
    version=version,
    description='Lense API platform common libraries',
    long_description=long_desc,
    author='David Taylor',
    author_email='djtaylor13@gmail.com',
    url='http://github.com/djtaylor/lense-common',
    license='GPLv3',
    packages=find_packages(),
    keywords='lense api common platform engine',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Terminals',
    ],
    install_requires = [
        'Django>=1.8.3',
        'feedback>=0.1',
        'django_auth_ldap>=1.2.6'
    ]
)