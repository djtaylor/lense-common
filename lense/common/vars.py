import os
import re
import sys
import platform

# Lense Libraries
from lense.common.collection import Collection

"""
Common attributes shared by various Lense modules. Defines string
constants, messages, system paths, and other shared information.
"""

# System Type
SYS_TYPE       = platform.system().lower()

# Cloudscape User
C_USER         = 'cloudscape'

# Static System Definitions
L_BASE         = os.getenv('HOME', '/home/cloudscape')

# Host types
H_LINUX        = 'linux'
H_WINDOWS      = 'windows'

# Cloudscape API Client
C_CLIENT       = '%s/python/cloudscape/client' % L_BASE

# Client input mapper
C_MAPPER       = '%s/conf/client/mapper.json' % L_BASE

# Server configuration / default configuration
S_CONF         = '%s/conf/server.conf' % L_BASE
S_CONF_DEF     = '%s/conf/default/server.conf' % L_BASE

# Administrator Group / User
G_ADMIN        = '00000000-0000-0000-0000-000000000000'
U_ADMIN        = 'cloudscape'

# Non-privileged Group / Default Group
G_USER         = '11111111-1111-1111-1111-111111111111'
G_DEFAULT      = G_USER

# API Templates
T_ROOT         = '%s/python/lense/engine/templates/api' % L_BASE
T_BASE         = '%s/base' % T_ROOT
T_ACL          = '%s/acl' % T_ROOT

# Account types
T_USER         = 'user'
T_HOST         = 'host'

# Log Directory
LOG_DIR        = '%s/log' % L_BASE

# Embedded Python paths
PY_BASE        = '%s/python' % L_BASE
