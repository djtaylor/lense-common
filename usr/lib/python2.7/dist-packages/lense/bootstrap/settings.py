from os import environ
from lense import get_applications
from lense.common.utils import rstring

# Debug mode
DEBUG            = True

# Secret key
SECRET_KEY       = rstring(64)

# Internationalization settings
LANGUAGE_CODE    = 'en-us'
TIME_ZONE        = 'UTC'
USE_I18N         = True
USE_L10N         = True
USE_TZ           = True

# API token lifetime in hours
API_TOKEN_LIFE   = 1

# URL processor
ROOT_URLCONF     = __name__

# Database connections
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     environ.get('BOOTSTRAP_DB_NAME', 'lense'),
        'USER':     environ.get('BOOTSTRAP_DB_USER', 'root'),
        'PASSWORD': environ.get('BOOTSTRAP_DB_PASS', None),
        'HOST':     environ.get('BOOTSTRAP_DB_HOST', 'localhost'),
        'PORT':     environ.get('BOOTSTRAP_DB_PORT', '3306')
    }
}

# Managed applications
INSTALLED_APPS = get_applications([
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
])

# Django middleware classes
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)