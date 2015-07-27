import os
import re
import sys
import platform

# Lense Libraries
from lense import PKG_ROOT
from lense.common.collection import Collection

"""
Common attributes shared by various Lense modules. Defines string
constants, messages, system paths, and other shared information.
"""

# Lense User
L_USER         = 'lense'

# Lense Configuration Files
LENSE_CONFIG   = Collection({
    'ENGINE': '{}/data/conf/engine.json'.format(PKG_ROOT),
    'PORTAL': '{}/data/conf/portal.json'.format(PKG_ROOT),
    'CLIENT': '{}/data/conf/client.json'.format(PKG_ROOT)
}).get()

# WSGI Configuration Files
WSGI_CONFIG    = Collection({
    'ENGINE': '{}/data/conf/apache/engine-wsgi.conf'.format(PKG_ROOT),
    'PORTAL': '{}/data/conf/apache/portal-wsgi.conf'.format(PKG_ROOT)                     
}).get()

# Log / PID Directory
LOG_DIR        = '/var/log/lense'
PID_DIR        = '/var/run/lense'

# Database encryption keys
DB_ENCRYPT_DIR = '{}/data/dbkey'.format(PKG_ROOT)

# Administrator Group / User
G_ADMIN        = '00000000-0000-0000-0000-000000000000'
U_ADMIN        = 'lense'

# Non-privileged Group / Default Group
G_USER         = '11111111-1111-1111-1111-111111111111'
G_DEFAULT      = G_USER

# API Templates
T_ROOT         = '{}/data/templates/engine/api'.format(PKG_ROOT)
T_BASE         = '{}/base'.format(T_ROOT)
T_ACL          = '{}/acl'.format(T_ROOT)