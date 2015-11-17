from lense.common.collection import Collection

"""
Common attributes shared by various Lense modules. Defines string
constants, messages, system paths, and other shared information.
"""

# Lense User
L_USER         = 'lense'

# Lense Configuration Files
LENSE_CONFIG   = Collection({
    'ENGINE': '/etc/lense/engine.conf',
    'PORTAL': '/etc/lense/portal.conf',
    'CLIENT': '/etc/lense/client.conf',
    'MAPPER': '/etc/lense/client.mapper.json',
    'SOCKET': '/etc/lense/socket.conf'
}).get()

# WSGI Configuration Files
WSGI_CONFIG    = Collection({
    'ENGINE': ['lense-engine', '/etc/apache2/sites-available/lense-engine.conf'],
    'PORTAL': ['lense-portal', '/etc/apache2/sites-available/lense-portal.conf']                    
}).get()

# Log / Run Directory
LOG_DIR        = '/var/log/lense'
RUN_DIR        = '/var/run/lense'

# Database encryption keys
DB_ENCRYPT_DIR = '/etc/lense/dbkey'

# Administrator Group / User
G_ADMIN        = '00000000-0000-0000-0000-000000000000'
U_ADMIN        = 'lense'

# Non-privileged Group / Default Group
G_USER         = '11111111-1111-1111-1111-111111111111'
G_DEFAULT      = G_USER

# API Templates
TEMPLATES      = Collection({
    'ENGINE': '/usr/share/lense/engine/templates',
    'PORTAL': '/usr/share/lense/portal/templates'                     
}).get()

# API Groups
GROUPS         = Collection({
    'SERVICE': {
        'UUID': '99999999-9999-9999-9999-999999999999',
        'NAME': 'service'
    },
    'ADMIN': {
        'UUID': '00000000-0000-0000-0000-000000000000',
        'NAME': 'admin'
    },
    'DEFAULT': {
        'UUID': '11111111-1111-1111-1111-111111111111',
        'NAME': 'default'
    }
}).get()

# API Users
USERS          = Collection({
    'SERVICE': {
        'GROUP': GROUPS.SERVICE.UUID,
        'NAME': 'service'
    },
    'ADMIN': {
        'GROUP': GROUPS.ADMIN.UUID,
        'NAME': 'lense'
    }
}).get()