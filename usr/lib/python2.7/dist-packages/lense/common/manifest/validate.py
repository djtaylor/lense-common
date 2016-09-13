from uuid import UUID
from re import compile
from six import string_types, integer_types
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# Lense Libraries
from lense.common.http import HTTP_METHODS
from lense.common.exceptions import ManifestError

# Data type mappings
TYPES = {
    'str': string_types,
    'int': integer_types,
    'bool': bool,
    'list': list,
    'dict': dict
}

class ManifestValidate(object):
    """
    Class object for containing methods for validating manifest attribute
    values.
    """
    @staticmethod
    def uuid(value):
        """
        Validate a UUID value.
        """
        try:
            UUID(value, version=4)
            return True
        except:
            return False

    @staticmethod
    def email(value):
        """
        Validate an email address.
        """
        try:
            validate_email(value)
            return True
        except ValidationError:
            return False

    @staticmethod
    def path(value):
        """
        Validate a request path.
        """
        return re.compile(r'^[^\/][a-zA-Z0-9\/]*[^\/]$').match(value)

    @staticmethod
    def name(value):
        """
        Validate a name string.
        """
        return re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]$').match(value)

    @staticmethod
    def method(value):
        """
        Validate a request method.
        """
        return False if not value in HTTP_METHODS else True

    @staticmethod
    def type(value, mapping):
        """
        Validate a variable against a data type mapping.
        """
        if not mapping in TYPES:
            raise ManifestError('Invalid type mapping: {0}'.format(mapping))

        # Verify the data type
        if not isinstance(value, TYPES[mapping]):
            return False
        return True
