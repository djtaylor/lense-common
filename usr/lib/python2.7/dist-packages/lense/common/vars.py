from lense import MODULE_ROOT
from lense.common.collection import Collection

"""
Common attributes shared by various Lense modules. Defines string
constants, messages, system paths, and other shared information.
"""

# Database encryption keys
DB_ENCRYPT_DIR = '/etc/lense/dbkey'

# Lense Configuration Files
CONFIG = Collection({
    'ENGINE': '/etc/lense/engine.conf',
    'PORTAL': '/etc/lense/portal.conf',
    'CLIENT': '/etc/lense/client.conf',
    'SOCKET': '/etc/lense/socket.conf',
    'BOOTSTRAP': '/etc/lense/bootstrap.conf'
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

# Request Handlers
HANDLERS = Collection({
    'ENGINE': {
        'DIR': '{0}/engine/api/handlers'.format(MODULE_ROOT),
        'MOD': 'lense.engine.api.handlers'
    },
    'PORTAL': {
        'DIR': '{0}/portal/ui/handlers'.format(MODULE_ROOT),
        'MOD': 'lense.portal.ui.handlers'
    },
    'CLIENT': {
        'DIR': '{0}/client/module'.format(MODULE_ROOT),
        'MOD': 'lense.client.module'
    }
}).get()

# Lense Projects
PROJECTS = Collection({
    'ENGINE': {
        'CONF': getattr(CONFIG, 'ENGINE'),
        'REQUEST': True,
        'OBJECTS': True,
        'AUTH': True
    },
    'PORTAL': {
        'CONF': getattr(CONFIG, 'PORTAL'),
        'REQUEST': True,
        'OBJECTS': True,
        'AUTH': True
    },
    'CLIENT': {
        'CONF': getattr(CONFIG, 'CLIENT'),
    },
    'SOCKET': {
        'CONF': getattr(CONFIG, 'SOCKET'),
        'RUN': '/var/run/lense',
        'PREFIX': '/usr/share/lense/socket'
    },
    'BOOTSTRAP': {
        'CONF': getattr(CONFIG, 'BOOTSTRAP'),
        'REQUEST': True,
        'OBJECTS': True
    }
}).get()

# API Groups
GROUPS = Collection({
    'ADMIN': {
        'UUID': '00000000-0000-0000-0000-000000000000',
        'NAME': 'administrators'
    },
    'USER': {
        'UUID': '11111111-1111-1111-1111-111111111111',
        'NAME': 'users'
    }
}).get()

# API Users
USERS = Collection({
    'ADMIN': {
        'GROUP': GROUPS.ADMIN.UUID,
        'NAME': 'admin',
        'UUID': '00000000-0000-0000-0000-111111111111'
    },
    'USER': {
        'GROUP': GROUPS.USER.UUID,
        'NAME': 'user',
        'UUID': '11111111-1111-1111-1111-222222222222'
    }
}).get()

# Share directories
SHARE = Collection({
    'BOOTSTRAP': '/usr/share/lense/bootstrap',
    'PORTAL': '/usr/share/lense/portal',
    'ENGINE': '/usr/share/lense/engine',
    'CLIENT': '/usr/share/lense/client',
    'SOCKET': '/usr/share/lense/socket'
}).get()