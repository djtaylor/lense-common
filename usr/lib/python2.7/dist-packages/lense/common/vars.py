from lense.common.collection import Collection

"""
Common attributes shared by various Lense modules. Defines string
constants, messages, system paths, and other shared information.
"""

# Lense User
L_USER         = 'lense'

# Lense Configuration Files
LENSE_CONFIG   = Collection({
    'ENGINE': '/etc/lense/engine/config.json',
    'PORTAL': '/etc/lense/portal/config.json',
    'CLIENT': '/etc/lense/client/config.json',
    'SOCKET': '/etc/lense/socket/config.json'
}).get()

# WSGI Configuration Files
WSGI_CONFIG    = Collection({
    'ENGINE': '/etc/lense/engine/wsgi.conf',
    'PORTAL': '/etc/lense/portal/wsgi.conf'                    
}).get()

# Log / PID Directory
LOG_DIR        = '/var/log/lense'
PID_DIR        = '/var/run/lense'

# Database encryption keys
DB_ENCRYPT_DIR = '/etc/lense/dbkey'

# Administrator Group / User
G_ADMIN        = '00000000-0000-0000-0000-000000000000'
U_ADMIN        = 'lense'

# Non-privileged Group / Default Group
G_USER         = '11111111-1111-1111-1111-111111111111'
G_DEFAULT      = G_USER

# API Templates
T_ROOT         = '/usr/share/lense/templates/engine/api'
T_BASE         = '{}/base'.format(T_ROOT)
T_ACL          = '{}/acl'.format(T_ROOT)