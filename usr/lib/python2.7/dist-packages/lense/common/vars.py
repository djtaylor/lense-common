from lense.common.collection import Collection

"""
Common attributes shared by various Lense modules. Defines string
constants, messages, system paths, and other shared information.
"""

# Lense Configuration Files
CONFIG = Collection({
    'ENGINE': '/etc/lense/engine.conf',
    'PORTAL': '/etc/lense/portal.conf',
    'CLIENT': '/etc/lense/client.conf',
    'SOCKET': '/etc/lense/socket.conf'
}).get()

# WSGI Configuration Files
WSGI_CONFIG = Collection({
    'ENGINE': ['lense-engine', '/etc/apache2/sites-available/lense-engine.conf'],
    'PORTAL': ['lense-portal', '/etc/apache2/sites-available/lense-portal.conf']                    
}).get()

# API Templates
TEMPLATES = Collection({
    'ENGINE': '/usr/share/lense/engine/templates',
    'PORTAL': '/usr/share/lense/portal/templates'                     
}).get()

# Lense Projects
PROJECTS = Collection({
    'ENGINE': {
        'LOG':  '/var/log/lense/engine.log',
        'CONF': '/etc/lense/engine.conf'
    },
    'PORTAL': {
        'LOG':  '/var/log/lense/portal.log',
        'CONF': '/etc/lense/portal.conf'
    },
    'CLIENT': {
        'LOG':  '/var/log/lense/client.log',
        'CONF': '/etc/lense/client.conf'
    },
    'SOCKET': {
        'LOG':  '/var/log/lense/socket.log',
        'CONF': '/etc/lense/socket.conf'
    }
})

# API Groups
GROUPS = Collection({
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
USERS = Collection({
    'SERVICE': {
        'GROUP': GROUPS.SERVICE.UUID,
        'NAME': 'service'
    },
    'ADMIN': {
        'GROUP': GROUPS.ADMIN.UUID,
        'NAME': 'lense'
    }
}).get()